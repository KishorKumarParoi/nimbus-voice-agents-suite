from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import AgentType, AgentMetadata
from backend.agents import get_agent, get_all_agent_metadata

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("", response_model=List[AgentMetadata])
async def list_agents():
    """Returns the full catalog of 5 specialized Nimbus voice agents."""
    return get_all_agent_metadata()

@router.get("/{agent_type}", response_model=AgentMetadata)
async def get_agent_details(agent_type: AgentType):
    all_agents = get_all_agent_metadata()
    for ag in all_agents:
        if ag.id == agent_type:
            return ag
    raise HTTPException(status_code=404, detail="Agent not found")
