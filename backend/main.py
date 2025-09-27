"""
AI Orchestrator Platform - Phase 0 MVP
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any

from app.api.agents import router as agents_router
from app.api.artifacts import router as artifacts_router
from app.api.workflows import router as workflows_router
from app.api.tasks import router as tasks_router
from app.core.config import settings
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # Startup
    logger.info("Starting AI Orchestrator Platform...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Register default agents
    from app.agents.registry import AgentRegistry
    registry = AgentRegistry()
    await registry.register_default_agents()
    logger.info("Default agents registered")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Orchestrator Platform...")

# Create FastAPI app
app = FastAPI(
    title="AI Orchestrator Platform",
    description="Phase 0 MVP - Agent orchestration with A2A protocol",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(artifacts_router, prefix="/api/v1/artifacts", tags=["artifacts"])
app.include_router(workflows_router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint - API status"""
    return {
        "status": "running",
        "name": "AI Orchestrator Platform",
        "version": "0.1.0",
        "phase": "Phase 0 MVP"
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )