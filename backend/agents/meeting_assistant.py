from typing import List, Dict, Any, Tuple, Optional
from backend.models import AgentType, ToolExecutionResult
from backend.agents.base import BaseVoiceAgent

class MeetingAssistantAgent(BaseVoiceAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.MEETING_ASSISTANT,
            name="Meeting Assistant",
            default_system_prompt=(
                "You are an executive real-time Meeting Assistant. "
                "You listen in on discussions, capture structured meeting notes, identify key decisions, "
                "and cleanly extract actionable items with owners and deadlines. "
                "Keep responses focused, structured, and action-oriented."
            )
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "log_meeting_note",
                    "description": "Records an important topic, update, or insight discussed during the meeting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "key_points": {"type": "string"}
                        },
                        "required": ["topic", "key_points"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_action_items",
                    "description": "Extracts concrete follow-up tasks, assignees, and target delivery dates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "Specific action item description"},
                            "assignee": {"type": "string", "description": "Person responsible"},
                            "deadline": {"type": "string", "description": "Target completion date or sprint"}
                        },
                        "required": ["task", "assignee"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_meeting_summary",
                    "description": "Compiles executive minutes and consensus decisions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agenda_item": {"type": "string"},
                            "decision_reached": {"type": "string"}
                        },
                        "required": ["decision_reached"]
                    }
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        if tool_name == "log_meeting_note":
            topic = arguments.get("topic", "General")
            notes = arguments.get("key_points", "")
            return {"status": "recorded", "topic": topic, "content": notes}, f"Note logged: [{topic}] {notes}"

        elif tool_name == "extract_action_items":
            task = arguments.get("task", "Follow up on action item")
            assignee = arguments.get("assignee", "Team Lead")
            deadline = arguments.get("deadline", "End of Sprint")
            return {
                "action_item_id": "ACT-104",
                "task": task,
                "assignee": assignee,
                "deadline": deadline,
                "status": "pending"
            }, f"Action Item: {assignee} to {task} by {deadline}"

        elif tool_name == "generate_meeting_summary":
            decision = arguments.get("decision_reached", "Approved")
            return {
                "status": "archived",
                "decision": decision
            }, f"Decision Finalized: {decision}"

        return {"error": "Unknown tool"}, None

    def _generate_fallback(self, user_message: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        msg = user_message.lower()
        if "action" in msg or "todo" in msg or "task" in msg or "assign" in msg:
            tool = ToolExecutionResult(
                tool_name="extract_action_items",
                arguments={"task": "Deploy multi-agent voice cluster to Vercel", "assignee": "Kishor", "deadline": "Today 6 PM"},
                output={"status": "assigned", "priority": "P0"},
                latency_ms=11.2
            )
            return (
                "Action item recorded: Kishor will oversee the multi-agent voice deployment by 6 PM today. I've logged it into the meeting dashboard.",
                [tool],
                ["Action: Kishor to deploy multi-agent voice cluster to Vercel (Today 6 PM)"]
            )
        elif "summarize" in msg or "summary" in msg or "recap" in msg:
            tool = ToolExecutionResult(
                tool_name="generate_meeting_summary",
                arguments={"decision_reached": "Architecture unanimously approved for production ship."},
                output={"status": "summary_ready"},
                latency_ms=15.0
            )
            return (
                "Meeting recap: The team reviewed the Nimbus voice pipeline, approved the low-latency streaming design, and agreed on a Vercel production deployment.",
                [tool],
                ["Recap: Architecture approved, LiveKit streaming verified"]
            )
        else:
            return (
                "I am actively listening to your meeting. You can speak freely; I am capturing key points and will flag action items whenever decisions are made.",
                [],
                []
            )

