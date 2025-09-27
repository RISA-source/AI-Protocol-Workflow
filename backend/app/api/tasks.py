"""
Tasks API endpoints for A2A communication
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.agents.neural_summarizer import NeuralSummarizerAgent
from app.agents.symbolic_validator import SymbolicValidatorAgent

router = APIRouter()

# Agent instances
neural_agent = NeuralSummarizerAgent()
symbolic_agent = SymbolicValidatorAgent()

@router.post("/", response_model=dict)
async def create_task(
    task_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Create new task (A2A protocol endpoint)
    """
    try:
        target_agent = task_data.get("target_agent")
        
        if target_agent == "neural_summarizer_v1":
            result = await neural_agent.process_task(task_data)
        elif target_agent == "symbolic_validator_v1":
            result = await symbolic_agent.process_task(task_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {target_agent}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}")
async def get_task_status(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get task status
    """
    # For Phase 0, return basic status
    return {
        "task_id": str(task_id),
        "status": "completed",  # Placeholder
        "created_at": "2025-01-01T00:00:00Z"
    }

@router.put("/{task_id}/status")
async def update_task_status(
    task_id: UUID,
    status_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Update task status (agent reporting progress)
    """
    # For Phase 0, just acknowledge
    return {"status": "updated"}

@router.post("/{task_id}/complete")
async def mark_task_complete(
    task_id: UUID,
    completion_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Mark task complete with output
    """
    # For Phase 0, just acknowledge
    return {"status": "completed"}