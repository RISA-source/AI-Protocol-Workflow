"""
Agent models for storing agent definitions and instances
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class AgentType(str, enum.Enum):
    """Agent types"""
    NEURAL = "neural"
    SYMBOLIC = "symbolic"
    META = "meta"
    EXTERNAL = "external"


class AgentStatus(str, enum.Enum):
    """Agent registration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class DeploymentType(str, enum.Enum):
    """Agent deployment types"""
    API = "api"
    LOCAL = "local"


class HealthStatus(str, enum.Enum):
    """Agent health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class Agent(Base):
    """
    Agent definition and capabilities
    """
    __tablename__ = "agents"
    
    agent_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(AgentType), nullable=False)
    version = Column(String(20), nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE)
    
    # Capabilities and configuration
    capabilities = Column(JSON, default=list)
    deployment_options = Column(JSON, default=dict)
    input_formats = Column(JSON, default=list)
    output_formats = Column(JSON, default=list)
    resource_requirements = Column(JSON, default=dict)
    reliability_metrics = Column(JSON, default=dict)
    agent_metadata = Column("metadata", JSON, default=dict)  # renamed to avoid reserved word
    
    # Timestamps
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    instances = relationship("AgentInstance", back_populates="agent", cascade="all, delete-orphan")


class AgentInstance(Base):
    """
    Agent deployment instances
    """
    __tablename__ = "agent_instances"
    
    instance_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(50), ForeignKey("agents.agent_id"), nullable=False)
    
    # Deployment details
    deployment_type = Column(Enum(DeploymentType), nullable=False)
    endpoint_url = Column(String(255))
    api_key_required = Column(Boolean, default=False)
    
    # Runtime metrics
    current_load = Column(Integer, default=0)
    max_concurrent_tasks = Column(Integer, default=1)
    last_health_check = Column(DateTime(timezone=True))
    status = Column(Enum(HealthStatus), default=HealthStatus.HEALTHY)
    
    # Relationships
    agent = relationship("Agent", back_populates="instances")
