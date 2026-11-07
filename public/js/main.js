document.addEventListener('DOMContentLoaded', async () => {
  const visualizer = new AudioWaveVisualizer('visualizerCanvas');

  // Agent meta mapping
  const agentIcons = {
    'receptionist': { icon: '📞', color: '#3b82f6', bg: '#eff6ff', desc: 'An intelligent phone receptionist that answers questions, routes calls, and handles bookings.' },
    'meeting_assistant': { icon: '📝', color: '#8b5cf6', bg: '#f5f3ff', desc: 'A real-time voice assistant that joins meetings, takes notes, and extracts action items.' },
    'research_assistant': { icon: '📖', color: '#ec4899', bg: '#fdf2f8', desc: 'A voice-driven research agent that searches, summarizes, and answers complex questions.' },
    'desktop_assistant': { icon: '🖥️', color: '#f97316', bg: '#fff7ed', desc: 'A personal voice assistant that controls your desktop, launches apps, and automates tasks.' },
    'scheduling_agent': { icon: '📅', color: '#10b981', bg: '#ecfdf5', desc: 'A voice agent that manages calendars, sets reminders, and coordinates meetings.' }
  };

  let activeAgent = 'receptionist';

  const engine = new VoiceEngine({
    agentType: activeAgent,
    visualizer: visualizer,
    onStatusChange: (status) => {
      const micBtn = document.getElementById('micBtn');
      const statusText = document.getElementById('engineStatusText');
      
      if (status === 'listening') {
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<span>🎙️ Listening...</span>';
        statusText.textContent = 'Agent Listening (Speak now)';
      } else if (status === 'thinking') {
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<span>⏳ Reasoning...</span>';
        statusText.textContent = 'Agent Reasoning (LLM + Tools)';
      } else if (status === 'speaking') {
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<span>🔊 Speaking...</span>';
        statusText.textContent = 'Audio Streaming (Barge-in active)';
      } else {
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<span>🎙️ Push to Talk</span>';
        statusText.textContent = 'Ready for Voice Input';
      }
    },
    onTranscript: (text, isFinal) => {
      if (isFinal) {
        addMessageBubble('user', text);
      }
    },
    onReply: (text) => {
      addMessageBubble('agent', text);
    },
    onLatency: (metrics) => {
      document.getElementById('asrMs').textContent = `${metrics.asr_ms} ms`;
      document.getElementById('llmMs').textContent = `${metrics.llm_ttft_ms} ms`;
      document.getElementById('ttsMs').textContent = `${metrics.tts_ttfb_ms} ms`;
      document.getElementById('totalMs').textContent = `${metrics.total_ms} ms`;

      // Update proportional bar widths
      const total = metrics.asr_ms + metrics.llm_ttft_ms + metrics.tts_ttfb_ms || 1;
      document.getElementById('barAsr').style.width = `${(metrics.asr_ms / total) * 100}%`;
      document.getElementById('barLlm').style.width = `${(metrics.llm_ttft_ms / total) * 100}%`;
      document.getElementById('barTts').style.width = `${(metrics.tts_ttfb_ms / total) * 100}%`;
    },
    onToolExecuted: (tool) => {
      addActionItem(`⚡ Tool executed: ${tool.tool_name} (${tool.latency_ms}ms)`);
    }
  });

  // UI Event bindings
  document.getElementById('micBtn').addEventListener('click', () => {
    engine.toggleListening();
  });

  document.getElementById('interruptBtn').addEventListener('click', () => {
    engine.bargeIn();
    addActionItem('⚠️ Conversation interrupted (Barge-in triggered)');
  });

  document.getElementById('testSimBtn').addEventListener('click', () => {
    const samples = {
      'receptionist': "Can you book a consultation for me at 2:30 PM?",
      'meeting_assistant': "Please extract action items from our morning review.",
      'research_assistant': "Compare WebRTC vs WebSocket latency for real-time voice streaming.",
      'desktop_assistant': "Check my current system telemetry and launch VS Code.",
      'scheduling_agent': "Schedule a 30-minute sync tomorrow at 11:00 AM."
    };
    const query = samples[activeAgent] || "Hello!";
    addMessageBubble('user', query);
    engine.sendTurn(query);
  });

  // Settings sync
  document.getElementById('ragSelect').addEventListener('change', (e) => {
    engine.useRag = e.target.value === 'rag';
    addActionItem(`Config: Switched to ${e.target.value.toUpperCase()} mode`);
  });

  document.getElementById('modeSelect').addEventListener('change', (e) => {
    engine.streaming = e.target.value === 'streaming';
    addActionItem(`Config: Switched to ${e.target.value.toUpperCase()} mode`);
  });

  document.getElementById('ttsSelect').addEventListener('change', (e) => {
    engine.ttsProvider = e.target.value;
    addActionItem(`Config: Switched TTS provider to ${e.target.value}`);
  });

  // LiveKit WebRTC Token Connect Button
  document.getElementById('livekitConnectBtn').addEventListener('click', async () => {
    const res = await engine.connectLiveKitRoom();
    if (res) {
      addActionItem(`🟢 LiveKit WebRTC Room Connected: ${res.room_name}`);
      alert(`LiveKit WebRTC Connected!\nRoom: ${res.room_name}\nParticipant: ${res.participant_identity}\nServer: ${res.server_url}`);
    } else {
      addActionItem(`🔴 LiveKit Connection Failed`);
    }
  });

  // Select Agent Click Handler
  window.selectAgent = (agentKey, agentName) => {
    activeAgent = agentKey;
    engine.agentType = agentKey;
    engine.bargeIn();

    document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
    const targetCard = document.getElementById(`card-${agentKey}`);
    if (targetCard) targetCard.classList.add('active');

    const meta = agentIcons[agentKey];
    document.getElementById('activeAgentAvatar').textContent = meta.icon;
    document.getElementById('activeAgentAvatar').style.backgroundColor = meta.bg;
    document.getElementById('activeAgentAvatar').style.color = meta.color;
    document.getElementById('activeAgentName').textContent = agentName;
    document.getElementById('activeAgentTagline').textContent = meta.desc;

    // Scroll smoothly to playground
    document.getElementById('playgroundSection').scrollIntoView({ behavior: 'smooth' });
    addActionItem(`Switched active voice agent to: ${agentName}`);
  };

  function addMessageBubble(role, text) {
    const list = document.getElementById('messagesList');
    const bubble = document.createElement('div');
    bubble.className = `msg-bubble ${role === 'user' ? 'msg-user' : 'msg-agent'}`;
    bubble.textContent = text;
    list.appendChild(bubble);
    list.scrollTop = list.scrollHeight;
  }

  function addActionItem(text) {
    const list = document.getElementById('actionsList');
    const card = document.createElement('div');
    card.className = 'action-card';
    card.textContent = text;
    list.prepend(card);
  }
});

