import re
import math
from typing import List, Dict, Any, Tuple

# Comprehensive knowledge bases for all 5 voice agents
AGENT_KNOWLEDGE_BASES = {
    "receptionist": [
        "Company Overview: Nimbus Enterprise Suite provides next-generation AI infrastructure, voice orchestration, and meeting workflows.",
        "Office Hours: Our customer operations and front desk operate Monday through Friday from 8:00 AM to 6:00 PM EST, and Saturday from 9:00 AM to 2:00 PM EST.",
        "Call Routing: Dial 1 for Sales & Enterprise Upgrades, Dial 2 for Technical Support & SRE, Dial 3 for Billing & Account Management.",
        "Pricing Plans: Nimbus Starter is $49/mo, Nimbus Pro is $199/mo, and Enterprise custom tier offers dedicated GPU clusters with SLA guarantees.",
        "Booking Policies: Appointments require at least 2 hours advance notice. Cancellations made 24 hours prior receive a 100% full refund.",
        "Location & HQ: Global Headquarters is at 500 Silicon Vista Blvd, San Francisco, CA. Regional EMEA hub located in London."
    ],
    "meeting_assistant": [
        "Meeting Protocol: Capture key decisions, action item assignees, target deadlines, and parking lot topics.",
        "Action Item Syntax: Assignee, specific task verb, deliverable, and explicit completion date or sprint milestone.",
        "Executive Summary Format: Context, 3-5 bulleted decisions, unblocking dependencies, next sync schedule.",
        "Speaker Diarization: Track multiple participant speech streams, isolating lead remarks and unanimous consensus.",
        "Integration: Direct sync capability with Notion, Slack, Jira, and Linear."
    ],
    "research_assistant": [
        "Literature Synthesis: Deep multi-source retrieval across arXiv, academic repositories, RFC technical standards, and whitepapers.",
        "Fact Verification: Cross-reference quantitative figures, latency benchmarks, and statistical claims against verified sources.",
        "Citation Standards: Provide author, year, primary findings, and confidence score for all generated claims.",
        "Technical Analysis: Evaluate algorithmic complexity, Big-O bounds, hardware tradeoffs, and architectural bottlenecks."
    ],
    "desktop_assistant": [
        "Safe Command Policy: Read-only inspection commands (ps, uptime, df, git status) run instantly; destructive commands (rm, drop) require user voice confirmation.",
        "Application Launching: Support for opening VS Code, Terminal, Chrome, Docker Desktop, Slack, and Figma via macOS open protocols.",
        "File Automation: Batch organization of downloads, workspace cleanup, log parsing, and environment variable audits.",
        "System Telemetry: Live monitoring of CPU utilization, RAM pressure, GPU VRAM allocation, and network socket activity."
    ],
    "scheduling_agent": [
        "Calendar Management: Integration with Google Calendar, Outlook 365, and Apple iCal via RFC 5545 iCalendar standard.",
        "Conflict Resolution: Automatic detection of double bookings, buffer time enforcement (15 min between meetings), and timezone normalization.",
        "Invite Dispatch: Automated generation of Google Meet and Zoom links with agenda bullets pre-populated in calendar descriptions.",
        "Working Hours Policy: Avoid scheduling meetings before 9:00 AM or after 5:30 PM local participant timezone unless flagged as high-priority emergency."
    ]
}

class SimpleRAGEngine:
    """
    Lightweight, deterministic vector retrieval engine.
    Calculates cosine similarity over term frequencies with stop-word filtering.
    """
    STOP_WORDS = {"the", "a", "an", "is", "in", "it", "to", "for", "and", "or", "of", "on", "at", "with", "this", "that"}

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if w not in self.STOP_WORDS]

    def _compute_vector(self, tokens: List[str]) -> Dict[str, float]:
        vec: Dict[str, float] = {}
        for t in tokens:
            vec[t] = vec.get(t, 0.0) + 1.0
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {k: v / norm for k, v in vec.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        score = 0.0
        for k, v in vec1.items():
            if k in vec2:
                score += v * vec2[k]
        return score

    def search(self, agent_type: str, query: str, top_k: int = 2) -> List[Tuple[str, float]]:
        docs = AGENT_KNOWLEDGE_BASES.get(agent_type, AGENT_KNOWLEDGE_BASES["receptionist"])
        query_vec = self._compute_vector(self._tokenize(query))

        ranked: List[Tuple[str, float]] = []
        for doc in docs:
            doc_vec = self._compute_vector(self._tokenize(doc))
            sim = self._cosine_similarity(query_vec, doc_vec)
            ranked.append((doc, round(sim, 4)))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def get_full_context_document(self, agent_type: str) -> str:
        """For RAG-less mode: inject full context document directly into prompt."""
        docs = AGENT_KNOWLEDGE_BASES.get(agent_type, AGENT_KNOWLEDGE_BASES["receptionist"])
        return "\n".join(f"- {d}" for d in docs)

rag_engine = SimpleRAGEngine()

