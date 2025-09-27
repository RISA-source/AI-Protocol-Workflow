"""
Workflow repository implementation
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from app.models.workflows import Workflow, Task, WorkflowStatus, TaskStatus
from app.core.database import get_db

class WorkflowRepository:
    """
    Repository for managing workflows and tasks
    """

    @asynccontextmanager
    async def get_db_session(self):
        """
        Async context manager to yield DB session
        """
        async for session in get_db():
            yield session

    async def create_workflow(self, name: str, description: str, workflow_definition: Dict[str, Any], total_steps: int) -> uuid.UUID:
        """
        Create new workflow and return its ID
        """
        async with self.get_db_session() as session:
            workflow_id = uuid.uuid4()

            workflow = Workflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                status=WorkflowStatus.RUNNING,
                workflow_definition=workflow_definition,
                total_steps=total_steps
            )

            session.add(workflow)
            await session.commit()
            return workflow_id

    async def update_workflow_status(self, workflow_id: uuid.UUID, status: WorkflowStatus, completed_steps: int = None, failed_steps: int = None):
        """
        Update workflow status
        """
        async with self.get_db_session() as session:
            stmt = select(Workflow).where(Workflow.workflow_id == workflow_id)
            result = await session.execute(stmt)
            workflow = result.scalar_one_or_none()

            if workflow:
                workflow.status = status
                if completed_steps is not None:
                    workflow.completed_steps = completed_steps
                if failed_steps is not None:
                    workflow.failed_steps = failed_steps
                if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                    workflow.completed_at = datetime.utcnow()
                await session.commit()

    async def create_task(self, workflow_id: uuid.UUID, agent_id: str, input_artifact_ids: List[str], parameters: Dict[str, Any]) -> uuid.UUID:
        """
        Create new task and return its ID
        """
        async with self.get_db_session() as session:
            task_id = uuid.uuid4()

            task = Task(
                task_id=task_id,
                workflow_id=workflow_id,
                agent_id=agent_id,
                status=TaskStatus.PENDING,
                input_artifact_ids=input_artifact_ids,
                parameters=parameters
            )

            session.add(task)
            await session.commit()
            return task_id

    async def update_task_status(self, task_id: uuid.UUID, status: TaskStatus, output_artifact_ids: List[str] = None, error_message: str = None):
        """
        Update task status
        """
        async with self.get_db_session() as session:
            stmt = select(Task).where(Task.task_id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if task:
                task.status = status
                if output_artifact_ids:
                    task.output_artifact_ids = output_artifact_ids
                if error_message:
                    task.error_message = error_message
                if status == TaskStatus.IN_PROGRESS:
                    task.started_at = datetime.utcnow()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.utcnow()
                await session.commit()

    async def get_workflow(self, workflow_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Get workflow by ID
        """
        async with self.get_db_session() as session:
            stmt = select(Workflow).where(Workflow.workflow_id == workflow_id)
            result = await session.execute(stmt)
            workflow = result.scalar_one_or_none()

            if not workflow:
                return None

            return {
                "workflow_id": str(workflow.workflow_id),
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status.value,
                "total_steps": workflow.total_steps,
                "completed_steps": workflow.completed_steps,
                "failed_steps": workflow.failed_steps,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
            }