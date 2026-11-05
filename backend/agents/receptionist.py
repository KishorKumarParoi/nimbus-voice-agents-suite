from typing import List, Dict, Any, Tuple, Optional
from backend.models import AgentType, ToolExecutionResult
from backend.agents.base import BaseVoiceAgent

class ReceptionistAgent(BaseVoiceAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.RECEPTIONIST,
            name="AI Receptionist",
            default_system_prompt=(
                "You are an intelligent phone receptionist for Nimbus Enterprise. "
                "You answer customer inquiries with elegance, route calls to departments (Sales, Support, Billing), "
                "and handle appointment bookings. Speak warmly, concisely, and clearly as if on a high-fidelity phone line."
            )
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_service_availability",
                    "description": "Checks available booking slots for services or consultations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Target date (e.g., today, tomorrow, YYYY-MM-DD)"},
                            "department": {"type": "string", "enum": ["Sales", "Support", "Billing", "Executive"]}
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_appointment",
                    "description": "Confirms and books a telephone or in-office consultation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "caller_name": {"type": "string", "description": "Full name of caller"},
                            "time_slot": {"type": "string", "description": "e.g., 2:30 PM"},
                            "service": {"type": "string", "description": "e.g., Enterprise Architecture Review"}
                        },
                        "required": ["caller_name", "time_slot"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "route_call",
                    "description": "Transfers the live caller to a human specialist department.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "department": {"type": "string", "enum": ["Sales", "Support", "Billing", "Tier3_Eng"]},
                            "reason": {"type": "string", "description": "Reason for transfer"}
                        },
                        "required": ["department"]
                    }
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        if tool_name == "check_service_availability":
            date = arguments.get("date", "today")
            dept = arguments.get("department", "Sales")
            return {
                "status": "available",
                "date": date,
                "department": dept,
                "available_slots": ["10:00 AM", "2:30 PM", "4:15 PM"]
            }, None

        elif tool_name == "book_appointment":
            name = arguments.get("caller_name", "Valued Guest")
            slot = arguments.get("time_slot", "2:30 PM")
            svc = arguments.get("service", "Consultation")
            return {
                "booking_id": "NB-8821",
                "status": "confirmed",
                "caller": name,
                "time": slot,
                "service": svc
            }, f"Booked consultation for {name} at {slot} ({svc})"

        elif tool_name == "route_call":
            dept = arguments.get("department", "Sales")
            return {
                "status": "transferred",
                "destination": f"+1-800-555-{dept.upper()}",
                "hold_music": "smooth_ambient"
            }, f"Routing caller to {dept} department"

        return {"error": "Unknown tool"}, None

    def _generate_fallback(self, user_message: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        msg = user_message.lower()
        if "book" in msg or "appointment" in msg:
            tool = ToolExecutionResult(
                tool_name="book_appointment",
                arguments={"caller_name": "Kishor", "time_slot": "2:30 PM", "service": "Executive Consultation"},
                output={"booking_id": "NB-8821", "status": "confirmed"},
                latency_ms=12.4
            )
            return (
                "I have booked your consultation for 2:30 PM today. A confirmation SMS with details has been dispatched.",
                [tool],
                ["Booked consultation for Kishor at 2:30 PM"]
            )
        elif "route" in msg or "transfer" in msg or "sales" in msg or "support" in msg:
            tool = ToolExecutionResult(
                tool_name="route_call",
                arguments={"department": "Sales", "reason": "Pricing inquiry"},
                output={"status": "transferred", "destination": "Ext 401"},
                latency_ms=8.1
            )
            return (
                "Connecting you straight through to our enterprise sales team now. Please hold for just a moment.",
                [tool],
                ["Routed call to Enterprise Sales"]
            )
        else:
            return (
                "Hello and welcome to Nimbus Enterprise! I'm your AI Receptionist. I can assist with appointment booking, pricing information, or connect you to our team. How may I direct your call?",
                [],
                []
            )
