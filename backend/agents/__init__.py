from typing import Dict, List
from backend.models import AgentType, AgentMetadata
from backend.agents.base import BaseVoiceAgent
from backend.agents.receptionist import ReceptionistAgent
from backend.agents.meeting_assistant import MeetingAssistantAgent
from backend.agents.research_assistant import ResearchAssistantAgent
from backend.agents.desktop_assistant import DesktopAssistantAgent
from backend.agents.scheduling_agent import SchedulingAgent

# Initialize instances
agent_instances: Dict[AgentType, BaseVoiceAgent] = {
    AgentType.RECEPTIONIST: ReceptionistAgent(),
    AgentType.MEETING_ASSISTANT: MeetingAssistantAgent(),
    AgentType.RESEARCH_ASSISTANT: ResearchAssistantAgent(),
    AgentType.DESKTOP_ASSISTANT: DesktopAssistantAgent(),
    AgentType.SCHEDULING_AGENT: SchedulingAgent(),
}

def get_agent(agent_type: AgentType) -> BaseVoiceAgent:
    return agent_instances.get(agent_type, agent_instances[AgentType.RECEPTIONIST])

def get_all_agent_metadata() -> List[AgentMetadata]:
    """Returns metadata for all 5 voice agents matching the user's interface."""
    return [
        AgentMetadata(
            id=AgentType.RECEPTIONIST,
            name="AI Receptionist",
            tagline="An intelligent phone receptionist that answers questions, routes calls, and handles bookings.",
            icon="phone",
            badge_color="#3b82f6", # Blue/lavender
            capabilities=["Call Routing", "Service Booking", "FAQ Lookups", "Department Transfer"],
            system_prompt=agent_instances[AgentType.RECEPTIONIST].default_system_prompt,
            sample_queries=[
                "Can I book a consultation for 2:30 PM today?",
                "What are your business hours and refund policies?",
                "Please route me to the enterprise sales department."
            ]
        ),
        AgentMetadata(
            id=AgentType.MEETING_ASSISTANT,
            name="Meeting Assistant",
            tagline="A real-time voice assistant that joins meetings, takes notes, and extracts action items.",
            icon="edit-3",
            badge_color="#8b5cf6", # Purple
            capabilities=["Live Note-Taking", "Action Item Extraction", "Meeting Recaps", "Decision Logging"],
            system_prompt=agent_instances[AgentType.MEETING_ASSISTANT].default_system_prompt,
            sample_queries=[
                "Extract the action items from our discussion so far.",
                "Log a note that we approved the low-latency voice pipeline.",
                "Give me a concise recap of the decisions made today."
            ]
        ),
        AgentMetadata(
            id=AgentType.RESEARCH_ASSISTANT,
            name="Research Assistant",
            tagline="A voice-driven research agent that searches, summarizes, and answers complex questions.",
            icon="book-open",
            badge_color="#ec4899", # Magenta
            capabilities=["Corpus Search", "Evidence Synthesis", "Latency Benchmarking", "Citation Formatting"],
            system_prompt=agent_instances[AgentType.RESEARCH_ASSISTANT].default_system_prompt,
            sample_queries=[
                "Compare WebRTC versus WebSocket latency for voice streaming.",
                "What is the typical time-to-first-byte for ElevenLabs Turbo v2?",
                "Synthesize current literature on real-time acoustic echo cancellation."
            ]
        ),
        AgentMetadata(
            id=AgentType.DESKTOP_ASSISTANT,
            name="Desktop Assistant",
            tagline="A personal voice assistant that controls your desktop, launches apps, and automates tasks.",
            icon="monitor",
            badge_color="#f97316", # Orange/coral
            capabilities=["Application Launching", "Telemetry Inspection", "Safe Automation", "Shell Scripting"],
            system_prompt=agent_instances[AgentType.DESKTOP_ASSISTANT].default_system_prompt,
            sample_queries=[
                "Launch VS Code and open my project workspace.",
                "Check system telemetry, CPU load, and RAM pressure.",
                "Run a git status audit and clean temporary files."
            ]
        ),
        AgentMetadata(
            id=AgentType.SCHEDULING_AGENT,
            name="Scheduling Agent",
            tagline="A voice agent that manages calendars, sets reminders, and coordinates meetings.",
            icon="calendar",
            badge_color="#10b981", # Green/emerald
            capabilities=["Calendar Synchronization", "Conflict Detection", "Invite Generation", "Voice Reminders"],
            system_prompt=agent_instances[AgentType.SCHEDULING_AGENT].default_system_prompt,
            sample_queries=[
                "Schedule a 30-minute sync tomorrow at 11 AM.",
                "Do I have any calendar conflicts on Friday afternoon?",
                "Set a reminder in 30 minutes to verify the production deployment."
            ]
        )
    ]

