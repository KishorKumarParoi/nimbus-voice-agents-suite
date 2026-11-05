class VoiceEngine {
  constructor(options = {}) {
    this.agentType = options.agentType || 'receptionist';
    this.visualizer = options.visualizer || null;
    this.onTranscript = options.onTranscript || (() => {});
    this.onReply = options.onReply || (() => {});
    this.onLatency = options.onLatency || (() => {});
    this.onToolExecuted = options.onToolExecuted || (() => {});
    this.onStatusChange = options.onStatusChange || (() => {});

    this.isListening = false;
    this.isPlayingAudio = false;
    this.currentAudioElement = null;
    this.recognition = null;
    this.messages = [];
    this.livekitRoom = null;

    // Config defaults
    this.useRag = false;
    this.streaming = true;
    this.ttsProvider = 'elevenlabs';
    this.responseLength = 'medium';
    this.endpointSilenceMs = 600;

    this.setupRecognition();
  }

  setupRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        this.onStatusChange('listening');
        if (this.visualizer) this.visualizer.start('#38bdf8');
      };

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        const text = finalTranscript || interimTranscript;
        if (text) {
          this.onTranscript(text, Boolean(finalTranscript));
        }

        if (finalTranscript) {
          this.sendTurn(finalTranscript);
        }
      };

      this.recognition.onerror = (err) => {
        console.warn('Speech recognition warning:', err.error);
        this.stopListening();
      };

      this.recognition.onend = () => {
        this.isListening = false;
        if (!this.isPlayingAudio) {
          this.onStatusChange('idle');
          if (this.visualizer) this.visualizer.stop();
        }
      };
    }
  }

  startListening() {
    // Stop any existing TTS playback immediately (Instant Barge-in)
    this.bargeIn();

    if (this.recognition) {
      try {
        this.recognition.start();
      } catch (e) {
        console.warn('Recognition start exception:', e);
      }
    } else {
      // Prompt user text if Web Speech API unsupported
      const manual = prompt('Speech recognition not available on this browser. Enter message:');
      if (manual) {
        this.onTranscript(manual, true);
        this.sendTurn(manual);
      }
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
    this.isListening = false;
    this.onStatusChange('idle');
    if (this.visualizer && !this.isPlayingAudio) this.visualizer.stop();
  }

  toggleListening() {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  bargeIn() {
    if (this.currentAudioElement) {
      this.currentAudioElement.pause();
      this.currentAudioElement = null;
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    this.isPlayingAudio = false;
    if (this.visualizer) this.visualizer.stop();
    this.onStatusChange('interrupted');
  }

  async sendTurn(transcript) {
    this.onStatusChange('thinking');
    if (this.visualizer) this.visualizer.start('#a855f7'); // Purple thinking wave

    this.messages.push({ role: 'user', content: transcript });

    try {
      const resp = await fetch('/api/voice/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: this.agentType,
          text: transcript,
          messages: this.messages,
          use_rag: this.useRag,
          streaming: this.streaming,
          tts_provider: this.ttsProvider,
          response_length: this.responseLength,
          endpoint_silence_ms: this.endpointSilenceMs
        })
      });

      if (!resp.ok) throw new Error('API process error');
      const data = await resp.json();

      this.messages.push({ role: 'assistant', content: data.reply });
      this.onReply(data.reply);
      this.onLatency(data.latency);

      if (data.tools_executed && data.tools_executed.length > 0) {
        data.tools_executed.forEach(t => this.onToolExecuted(t));
      }

      // Play audio response
      this.playResponse(data.reply, data.audio_base64);

    } catch (err) {
      console.error('Turn processing failed:', err);
      this.onReply('I encountered a processing delay. Please try speaking again.');
      this.onStatusChange('idle');
      if (this.visualizer) this.visualizer.stop();
    }
  }

  playResponse(text, audioDataUri) {
    this.onStatusChange('speaking');
    this.isPlayingAudio = true;
    if (this.visualizer) this.visualizer.start('#10b981'); // Emerald speaking wave

    if (audioDataUri) {
      this.currentAudioElement = new Audio(audioDataUri);
      this.currentAudioElement.onended = () => {
        this.isPlayingAudio = false;
        this.onStatusChange('idle');
        if (this.visualizer) this.visualizer.stop();
      };
      this.currentAudioElement.play().catch(() => this.fallbackSpeak(text));
    } else {
      this.fallbackSpeak(text);
    }
  }

  fallbackSpeak(text) {
    if ('speechSynthesis' in window) {
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1.05;
      utter.onend = () => {
        this.isPlayingAudio = false;
        this.onStatusChange('idle');
        if (this.visualizer) this.visualizer.stop();
      };
      window.speechSynthesis.speak(utter);
    } else {
      this.isPlayingAudio = false;
      this.onStatusChange('idle');
      if (this.visualizer) this.visualizer.stop();
    }
  }

  async connectLiveKitRoom() {
    try {
      const roomName = `room-${this.agentType}-${Date.now().toString(36)}`;
      const identity = `user-${Math.random().toString(36).substring(2, 8)}`;
      const resp = await fetch('/api/voice/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: roomName,
          participant_identity: identity,
          agent_type: this.agentType
        })
      });
      const data = await resp.json();
      return data;
    } catch (e) {
      console.error('Failed to mint LiveKit token:', e);
      return null;
    }
  }
}
