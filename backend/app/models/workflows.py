"""
Workflow models for tracking execution state and metrics
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base

class WorkflowStatus(str, enum.Enum):
    """Workflow execution status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class Workflow(Base):
    """
    Workflow context and execution tracking
    """
    __tablename__ = "workflows"
    
    workflow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.RUNNING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(100))  # User ID or system identifier
    workflow_definition = Column(JSON)  # Store the original workflow steps
    
    # Metrics
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    failed_steps = Column(Integer, default=0)
    
    # Relationships
    artifacts = relationship("Artifact", back_populates="workflow", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="workflow", cascade="all, delete-orphan")

class TaskStatus(str, enum.Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
    """
    Individual task within a workflow
    """
    __tablename__ = "tasks"
    
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id"), nullable=False)
    agent_id = Column(String(50), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Task details
    input_artifact_ids = Column(JSON, default=list)
    output_artifact_ids = Column(JSON, default=list)
    parameters = Column(JSON, default=dict)
    
    # Execution metrics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_time_ms = Column(Integer)
    retry_count = Column(Integer, default=0)
    
    # Error handling
    error_code = Column(String(50))
    error_message = Column(Text)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="tasks")