"""
Agents API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db

router = APIRouter()

# Static agent definitions for Phase 0
AGENTS = [
    {
        "agent_id": "neural_summarizer_v1",
        "name": "Text Summarization Agent",
        "type": "neural",
        "version": "1.0.0",
        "capabilities": ["text_summarization"],
        "input_formats": ["text/plain"],
        "output_formats": ["text/plain"],
        "status": "active"
    },
    {
        "agent_id": "symbolic_validator_v1",
        "name": "Logic Validation Agent",
        "type": "symbolic",
        "version": "1.0.0",
        "capabilities": ["schema_validation", "consistency_checking"],
        "input_formats": ["application/json", "text/plain"],
        "output_formats": ["application/json"],
        "status": "active"
    },
    {
        "agent_id": "meta_supervisor_v1",
        "name": "Workflow Supervisor Agent",
        "type": "meta",
        "version": "1.0.0",
        "capabilities": ["workflow_monitoring", "task_routing", "error_detection_and_recovery"],
        "input_formats": ["application/json"],
        "output_formats": ["application/json"],
        "status": "active"
    }
]

@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """
    List all available agents
    """
    return AGENTS

@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get agent details
    """
    for agent in AGENTS:
        if agent["agent_id"] == agent_id:
            return agent
    
    raise HTTPException(status_code=404, detail="Agent not found")

@router.get("/{agent_id}/health")
async def get_agent_health(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get agent health status
    """
    # For Phase 0, all agents are healthy
    return {"status": "healthy", "agent_id": agent_id}