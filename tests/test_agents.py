import pytest
from backend.models import AgentType

def test_health_check(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agents_count"] == 5

def test_system_status(client):
    response = client.get("/api/system-status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "livekit_connected" in data["providers"]
    assert len(data["supported_agents"]) == 5

def test_list_agents(client):
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 5
    agent_ids = [a["id"] for a in agents]
    assert "receptionist" in agent_ids
    assert "meeting_assistant" in agent_ids
    assert "research_assistant" in agent_ids
    assert "desktop_assistant" in agent_ids
    assert "scheduling_agent" in agent_ids

def test_get_specific_agent(client):
    response = client.get("/api/agents/receptionist")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Receptionist"
    assert "Call Routing" in data["capabilities"]

def test_livekit_token_generation(client):
    payload = {
        "room_name": "test-room-101",
        "participant_identity": "tester-1",
        "participant_name": "Test User",
        "agent_type": "receptionist"
    }
    response = client.post("/api/voice/token", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"].split(".")) == 3  # Valid JWT format
    assert data["room_name"] == "test-room-101"

def test_voice_process_receptionist(client):
    payload = {
        "agent_type": "receptionist",
        "text": "Can you book an appointment for me at 2:30 PM?",
        "messages": [],
        "use_rag": False,
        "tts_provider": "browser"
    }
    response = client.post("/api/voice/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "receptionist"
    assert len(data["reply"]) > 0
    assert data["latency"]["total_ms"] > 0

def test_voice_process_meeting_assistant(client):
    payload = {
        "agent_type": "meeting_assistant",
        "text": "Extract the action items from our discussion so far.",
        "messages": [],
        "use_rag": True,
        "tts_provider": "browser"
    }
    response = client.post("/api/voice/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "meeting_assistant"
    assert len(data["reply"]) > 0
    assert data["rag_used"] is True

def test_voice_process_research_assistant(client):
    payload = {
        "agent_type": "research_assistant",
        "text": "Compare WebRTC versus WebSocket latency for live voice streaming.",
        "messages": [],
        "use_rag": False,
        "tts_provider": "browser"
    }
    response = client.post("/api/voice/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "research_assistant"
    assert len(data["reply"]) > 0

def test_voice_process_desktop_assistant(client):
    payload = {
        "agent_type": "desktop_assistant",
        "text": "Launch VS Code and check system stats.",
        "messages": [],
        "use_rag": False,
        "tts_provider": "browser"
    }
    response = client.post("/api/voice/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "desktop_assistant"
    assert len(data["reply"]) > 0

def test_voice_process_scheduling_agent(client):
    payload = {
        "agent_type": "scheduling_agent",
        "text": "Schedule a 30-minute sync tomorrow at 11 AM.",
        "messages": [],
        "use_rag": False,
        "tts_provider": "browser"
    }
    response = client.post("/api/voice/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "scheduling_agent"
    assert len(data["reply"]) > 0

