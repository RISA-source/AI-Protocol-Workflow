"""
Artifacts API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.repositories.artifact_repository import ArtifactRepository
from app.models.artifacts import ValidationStatus

router = APIRouter()

@router.post("/", response_model=dict)
async def create_artifact(
    source_agent_id: str,
    workflow_id: UUID,
    task_id: UUID,
    content: str,
    content_type: str,
    parent_artifact_ids: Optional[List[UUID]] = None,
    metadata: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new artifact
    """
    try:
        repo = ArtifactRepository()
        artifact_id = await repo.create_artifact(
            source_agent_id=source_agent_id,
            workflow_id=workflow_id,
            task_id=task_id,
            content=content,
            content_type=content_type,
            parent_artifact_ids=parent_artifact_ids,
            metadata=metadata
        )
        
        return {"artifact_id": artifact_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{artifact_id}")
async def get_artifact(artifact_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve artifact by ID
    """
    repo = ArtifactRepository()
    artifact = await repo.get_artifact(artifact_id)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return artifact

@router.get("/{artifact_id}/lineage")
async def get_artifact_lineage(artifact_id: UUID, direction: str = "both", db: AsyncSession = Depends(get_db)):
    """
    Get artifact lineage (parents and children)
    """
    repo = ArtifactRepository()
    lineage = await repo.get_lineage(artifact_id, direction)
    return lineage

@router.get("/workflows/{workflow_id}/artifacts")
async def get_workflow_artifacts(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get all artifacts for a workflow
    """
    repo = ArtifactRepository()
    artifacts = await repo.get_workflow_artifacts(workflow_id)
    return {"artifacts": artifacts}

@router.put("/{artifact_id}/validate")
async def validate_artifact(
    artifact_id: UUID,
    status: str,
    details: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update artifact validation status
    """
    try:
        validation_status = ValidationStatus(status)
        repo = ArtifactRepository()
        await repo.update_validation_status(artifact_id, validation_status, details or {})
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid validation status: {status}")