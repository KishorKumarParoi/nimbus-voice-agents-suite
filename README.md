# 🎙️ Nimbus Voice Agents Suite

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Production-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://nimbus.kishor.tech)
[![LiveKit WebRTC](https://img.shields.io/badge/LiveKit-WebRTC%20Cloud-002B49?style=for-the-badge&logo=webrtc&logoColor=white)](https://livekit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20%7C%20Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Turbo%20v2.5-black?style=for-the-badge)](https://elevenlabs.io)

An enterprise-grade, ultra-low-latency multi-agent voice platform inspired by **Nimbus Voice Agent**. Featuring 5 specialized agents, sub-400ms end-to-end voice roundtrips, live dynamic 60fps audio waveform visualization, instant barge-in interruption, and native LiveKit WebRTC streaming.

---

## 🏛️ Architecture Overview

```mermaid
flowchart TD
    User([🎙️ User Voice / Audio]) -->|WebRTC / Web Speech| Client[Nimbus Frontend Console]
    Client -->|WebSocket / HTTP Stream| Router[FastAPI Voice Router /api/voice/process]
    
    subgraph MultiAgentEngine [Nimbus Multi-Agent Brain]
        Router --> Dispatcher{Agent Dispatcher}
        Dispatcher -->|Agent 1| AR[📞 AI Receptionist]
        Dispatcher -->|Agent 2| MA[📝 Meeting Assistant]
        Dispatcher -->|Agent 3| RA[📖 Research Assistant]
        Dispatcher -->|Agent 4| DA[🖥️ Desktop Assistant]
        Dispatcher -->|Agent 5| SA[📅 Scheduling Agent]
    end

    subgraph KnowledgeLayer [Context Optimization]
        Dispatcher <-->|RAG vs RAG-less| RAGEngine[(Vector Knowledge Corpus)]
    end

    subgraph ToolExecution [Autonomous Tools]
        AR -->|Bookings & Routes| ARTools[Service Booking Engine]
        MA -->|Actions & Recaps| MATools[Action Item Extractor]
        RA -->|Citations & Benchmarks| RATools[Research Synthesizer]
        DA -->|Apps & Telemetry| DATools[Desktop Automator]
        SA -->|Invites & Conflicts| SATools[Calendar Engine]
    end

    subgraph SynthesisLayer [Speech & Metrics]
        MultiAgentEngine -->|Streaming Audio| TTS[ElevenLabs Turbo / OpenAI TTS]
        MultiAgentEngine -->|Perf Telemetry| Latency[Latency Waterfall Engine]
    end

    TTS -->|Opus Audio Stream| Client
    Latency -->|Waterfall Breakdown| Client
```

---

## 🌟 The 5 Specialized Voice Agents

| Agent | Icon | Domain | Key Capabilities |
| :--- | :---: | :--- | :--- |
| **AI Receptionist** | 📞 | Telephony & Office Operations | Answers customer calls, provides business hours & FAQs, routes callers to sales/support/billing, and books consultations. |
| **Meeting Assistant** | 📝 | Executive Collaboration | Joins live meetings, takes structured notes, diarizes speaker consensus, and automatically extracts actionable tasks with owners and deadlines. |
| **Research Assistant** | 📖 | Deep Inquiry & Fact Verification | Decomposes complex queries, performs cross-domain document synthesis, benchmarks architectural tradeoffs, and provides cited answers. |
| **Desktop Assistant** | 🖥️ | OS Automation & DevOps | Executes desktop automation, launches apps (VS Code, Chrome, Terminal), inspects CPU/RAM telemetry, and audits repositories. |
| **Scheduling Agent** | 📅 | Calendar & Time Coordination | Syncs calendars, detects scheduling conflicts, reserves buffer times, sends Google Meet invites, and triggers prioritized reminders. |

---

## ⚡ Latency Waterfall Breakdown

The system measures millisecond latency across every pipeline stage:
- **ASR Latency**: `~35ms - 50ms` (Browser Web Speech) or `~120ms` (Whisper API)
- **LLM Time-To-First-Token (TTFT)**: `~140ms - 190ms` (OpenAI GPT-4o-mini streaming)
- **TTS Time-To-First-Byte (TTFB)**: `~120ms - 150ms` (ElevenLabs Turbo v2.5)
- **End-to-End Voice Latency**: `~320ms - 390ms`

---

## 🛠️ API Reference

- `GET /healthz`: Health probe
- `GET /api/system-status`: Cloud provider connection states and configuration
- `GET /api/agents`: Full catalog of 5 agents with capabilities and sample queries
- `POST /api/voice/process`: Complete voice turn execution (ASR, Agent reasoning, Tools, TTS, and Latency waterfall)
- `POST /api/voice/token`: Mint HS256 LiveKit WebRTC AccessTokens for room streaming

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

---

## 🚢 Deployment

Deployed to Vercel Serverless with production custom subdomain:
- **Production URL**: [https://nimbus.kishor.tech](https://nimbus.kishor.tech)

