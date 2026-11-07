class AudioWaveVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.animationId = null;
    this.analyser = null;
    this.dataArray = null;
    this.isActive = false;
    this.phase = 0;
    this.color = '#38bdf8'; // Cyan wave
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.drawIdle();
  }

  resize() {
    if (!this.canvas) return;
    this.canvas.width = this.canvas.offsetWidth * window.devicePixelRatio || 600;
    this.canvas.height = this.canvas.offsetHeight * window.devicePixelRatio || 120;
  }

  setAnalyser(analyserNode) {
    this.analyser = analyserNode;
    if (this.analyser) {
      this.analyser.fftSize = 256;
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);
    }
  }

  start(color = '#38bdf8') {
    this.color = color;
    this.isActive = true;
    this.animate();
  }

  stop() {
    this.isActive = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    this.drawIdle();
  }

  drawIdle() {
    if (!this.ctx) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);

    // Subtle gentle center line
    this.ctx.beginPath();
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    this.ctx.lineWidth = 2 * (window.devicePixelRatio || 1);
    this.ctx.moveTo(0, h / 2);
    this.ctx.lineTo(w, h / 2);
    this.ctx.stroke();
  }

  animate() {
    if (!this.isActive) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);

    let volumeMultiplier = 0.5;
    if (this.analyser && this.dataArray) {
      this.analyser.getByteFrequencyData(this.dataArray);
      let sum = 0;
      for (let i = 0; i < this.dataArray.length; i++) {
        sum += this.dataArray[i];
      }
      const avg = sum / this.dataArray.length;
      volumeMultiplier = Math.max(0.2, avg / 60);
    }

    this.phase += 0.08;

    // Render multi-layered glowing sine waves
    const layers = [
      { amp: 28 * volumeMultiplier, freq: 0.015, speed: 1.0, alpha: 0.9, color: this.color },
      { amp: 18 * volumeMultiplier, freq: 0.025, speed: -0.7, alpha: 0.5, color: '#818cf8' },
      { amp: 38 * volumeMultiplier, freq: 0.008, speed: 0.4, alpha: 0.3, color: '#c084fc' }
    ];

    layers.forEach(l => {
      this.ctx.beginPath();
      this.ctx.lineWidth = 3 * (window.devicePixelRatio || 1);
      this.ctx.strokeStyle = l.color;
      this.ctx.shadowColor = l.color;
      this.ctx.shadowBlur = 12;

      for (let x = 0; x < w; x += 4) {
        const y = (h / 2) + Math.sin(x * l.freq + this.phase * l.speed) * l.amp * Math.sin(x / w * Math.PI);
        if (x === 0) this.ctx.moveTo(x, y);
        else this.ctx.lineTo(x, y);
      }
      this.ctx.stroke();
    });

    this.animationId = requestAnimationFrame(() => this.animate());
  }
}

