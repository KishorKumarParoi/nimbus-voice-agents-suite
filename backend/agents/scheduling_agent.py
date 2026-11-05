from typing import List, Dict, Any, Tuple, Optional
from backend.models import AgentType, ToolExecutionResult
from backend.agents.base import BaseVoiceAgent

class SchedulingAgent(BaseVoiceAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.SCHEDULING_AGENT,
            name="Scheduling Agent",
            default_system_prompt=(
                "You are an executive Scheduling Agent. "
                "You coordinate calendars, detect overlapping conflicts, schedule calendar events, "
                "and set voice reminders. Always confirm attendees, times, and agendas with courteous precision."
            )
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_calendar_conflicts",
                    "description": "Scans existing calendar events to identify conflicts or open availability windows.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Target date (e.g., today, tomorrow, Friday)"},
                            "duration_minutes": {"type": "integer", "default": 30}
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_calendar_invite",
                    "description": "Creates a new calendar event with Google Meet / Zoom link and invites attendees.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "start_time": {"type": "string"},
                            "attendees": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["title", "start_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_reminder",
                    "description": "Sets a prioritized reminder or push notification.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reminder_text": {"type": "string"},
                            "trigger_time": {"type": "string"}
                        },
                        "required": ["reminder_text", "trigger_time"]
                    }
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        if tool_name == "check_calendar_conflicts":
            date = arguments.get("date", "today")
            return {
                "conflicts_found": 0,
                "date": date,
                "free_windows": ["11:00 AM - 12:00 PM", "3:00 PM - 4:30 PM", "5:00 PM - 6:00 PM"]
            }, None

        elif tool_name == "create_calendar_invite":
            title = arguments.get("title", "Sync")
            time_str = arguments.get("start_time", "3:00 PM")
            return {
                "event_id": "cal_evt_77192",
                "status": "confirmed",
                "meet_url": "https://meet.google.com/nmb-voic-agn",
                "title": title,
                "time": time_str
            }, f"Scheduled '{title}' at {time_str} (Google Meet link generated)"

        elif tool_name == "set_reminder":
            text = arguments.get("reminder_text", "Task")
            time_str = arguments.get("trigger_time", "1 hour")
            return {
                "reminder_id": "rem_9912",
                "status": "active",
                "text": text,
                "time": time_str
            }, f"Reminder set: '{text}' in {time_str}"

        return {"error": "Unknown tool"}, None

    def _generate_fallback(self, user_message: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        msg = user_message.lower()
        if "schedule" in msg or "calendar" in msg or "meet" in msg:
            tool = ToolExecutionResult(
                tool_name="create_calendar_invite",
                arguments={"title": "Sprint Review & Multi-Agent Demo", "start_time": "Tomorrow at 11:00 AM"},
                output={"status": "scheduled", "meet_url": "https://meet.google.com/nmb-voic-agn"},
                latency_ms=14.1
            )
            return (
                "Done. I've scheduled your Sprint Review and Multi-Agent Demo for tomorrow at 11:00 AM with a Google Meet invite attached.",
                [tool],
                ["Calendar Invite Created: Sprint Review & Demo (Tomorrow 11:00 AM)"]
            )
        elif "remind" in msg:
            tool = ToolExecutionResult(
                tool_name="set_reminder",
                arguments={"reminder_text": "Verify Vercel production deployment", "trigger_time": "in 30 minutes"},
                output={"status": "active"},
                latency_ms=7.9
            )
            return (
                "Reminder set for 30 minutes from now to verify the Vercel production deployment.",
                [tool],
                ["Reminder Set: Verify Vercel production deployment (30 mins)"]
            )
        else:
            return (
                "I am your Scheduling Agent. Tell me who you'd like to meet with, what time slot you prefer, or ask me to check your calendar for conflicts.",
                [],
                []
            )
