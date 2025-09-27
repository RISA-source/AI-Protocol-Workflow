"""
Configuration settings for the AI Orchestrator Platform
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "AI Orchestrator Platform"
    DEBUG: bool = True
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:Postgres%40123%25%3F@localhost:5432/ai_orchestrator_dev"
    
    # Security (simplified for Phase 0)
    SECRET_KEY: str = "phase0-development-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = 60
    MAX_RETRIES: int = 2
    RETRY_DELAY_SECONDS: int = 5
    
    # Artifact Storage
    ARTIFACT_STORAGE_TYPE: str = "filesystem"  # filesystem or s3
    ARTIFACT_BASE_PATH: str = "./artifacts"
    MAX_INLINE_SIZE: int = 10240  # 10KB
    
    # Meta-Agent Settings
    MAX_CONCURRENT_WORKFLOWS: int = 5
    HEALTH_CHECK_INTERVAL: int = 30
    POLL_INTERVAL: int = 2
    
    # OpenAI API (optional for neural agents)
    OPENAI_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create artifact directory if it doesn't exist
Path(settings.ARTIFACT_BASE_PATH).mkdir(parents=True, exist_ok=True)