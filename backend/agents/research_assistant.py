from typing import List, Dict, Any, Tuple, Optional
from backend.models import AgentType, ToolExecutionResult
from backend.agents.base import BaseVoiceAgent

class ResearchAssistantAgent(BaseVoiceAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.RESEARCH_ASSISTANT,
            name="Research Assistant",
            default_system_prompt=(
                "You are an analytical voice-driven Research Assistant. "
                "You perform deep technical searches, decompose multi-part queries, synthesize complex evidence, "
                "and articulate crisp, cited answers for audio listening. Cite concrete numbers, latency specs, and sources."
            )
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_research_corpus",
                    "description": "Searches academic papers, technical documentation, and benchmarking data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Technical search query"},
                            "domain": {"type": "string", "enum": ["ai_ml", "systems", "finance", "cloud_infra"]}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "synthesize_findings",
                    "description": "Synthesizes multi-source research into an executive briefing bullet list.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "key_evidence": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["topic", "key_evidence"]
                    }
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        if tool_name == "search_research_corpus":
            query = arguments.get("query", "voice agent architectures")
            return {
                "results_count": 3,
                "matches": [
                    {"title": "Streaming TTS & ASR Pipelines for Low Latency", "year": 2025, "p99_latency": "380ms"},
                    {"title": "WebRTC vs WebSocket for Conversational AI", "year": 2024, "packet_loss_recovery": "Adaptive Opus"}
                ]
            }, f"Corpus Search: Found verified papers for '{query}'"

        elif tool_name == "synthesize_findings":
            topic = arguments.get("topic", "Research Findings")
            return {"status": "synthesized", "topic": topic}, f"Briefing compiled on '{topic}'"

        return {"error": "Unknown tool"}, None

    def _generate_fallback(self, user_message: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        msg = user_message.lower()
        if "compare" in msg or "latency" in msg or "webrtc" in msg or "websocket" in msg:
            tool = ToolExecutionResult(
                tool_name="search_research_corpus",
                arguments={"query": "WebRTC vs WebSocket voice latency", "domain": "systems"},
                output={"webrtc_latency": "180ms", "websocket_latency": "420ms", "recommendation": "WebRTC with Opus RTP"},
                latency_ms=18.6
            )
            return (
                "According to recent benchmarks, WebRTC delivers median roundtrip latencies under 200 milliseconds by avoiding TCP retransmission delays, outperforming traditional WebSockets by nearly 60 percent.",
                [tool],
                ["Synthesized comparative latency: WebRTC (~180ms) vs WebSocket (~420ms)"]
            )
        else:
            return (
                "I am your Research Assistant. Ask me to investigate architectural tradeoffs, paper citations, or technical benchmarks, and I'll deliver evidence-backed answers.",
                [],
                []
            )

