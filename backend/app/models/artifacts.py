"""
Artifact models for storing workflow outputs with lineage tracking
"""

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base

class ContentCategory(str, enum.Enum):
    """Artifact content categories"""
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    IMAGE = "image"
    DOCUMENT = "document"
    BINARY = "binary"

class StorageType(str, enum.Enum):
    """Storage location types"""
    INLINE = "inline"
    FILESYSTEM = "filesystem"
    S3 = "s3"

class ValidationStatus(str, enum.Enum):
    """Artifact validation status"""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"

class Artifact(Base):
    """
    Main artifact table for storing workflow outputs
    """
    __tablename__ = "artifacts"
    
    # Identity
    artifact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_artifact_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    version = Column(Integer, default=1)
    
    # Provenance
    source_agent_id = Column(String(50), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Content Classification
    content_type = Column(String(100), nullable=False)  # MIME type or custom
    content_category = Column(Enum(ContentCategory), nullable=False)
    size_bytes = Column(Integer, default=0)
    
    # Storage Location
    storage_type = Column(Enum(StorageType), default=StorageType.INLINE)
    storage_path = Column(String(500))  # File path or S3 key
    content_text = Column(Text)  # Inline storage for small text
    
    # Metadata
    title = Column(String(200))
    description = Column(Text)
    tags = Column(ARRAY(String(100)), default=list)
    custom_metadata = Column(JSON, default=dict)
    
    # Quality & Validation
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    validation_details = Column(JSON, default=dict)
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    # Relationships
    workflow = relationship("Workflow", back_populates="artifacts")
    dependencies = relationship("ArtifactDependency", 
                               foreign_keys="ArtifactDependency.child_artifact_id",
                               back_populates="child")
    dependents = relationship("ArtifactDependency",
                            foreign_keys="ArtifactDependency.parent_artifact_id",
                            back_populates="parent")

class DependencyType(str, enum.Enum):
    """Types of artifact dependencies"""
    DIRECT_INPUT = "direct_input"
    REFERENCE = "reference"
    DERIVED_FROM = "derived_from"
    VALIDATED_BY = "validated_by"

class ArtifactDependency(Base):
    """
    Explicit dependency tracking for artifact DAG
    """
    __tablename__ = "artifact_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    parent_artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(Enum(DependencyType), default=DependencyType.DIRECT_INPUT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    child = relationship("Artifact", foreign_keys=[child_artifact_id], back_populates="dependencies")
    parent = relationship("Artifact", foreign_keys=[parent_artifact_id], back_populates="dependents")