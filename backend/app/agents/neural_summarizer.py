"""
Neural Summarizer Agent - Phase 0 MVP implementation
"""

import uuid
import time
import json
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.repositories.artifact_repository import ArtifactRepository

class NeuralSummarizerAgent:
    """
    Text summarization agent using OpenAI API
    """
    
    def __init__(self):
        self.agent_id = "neural_summarizer_v1"
        self.endpoint = "http://localhost:8001"  # Self-hosted endpoint for this agent
        self.artifact_repo = ArtifactRepository()
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a summarization task
        """
        try:
            # Extract input data
            task_id = task_data.get("task_id")
            workflow_id = task_data.get("workflow_id")
            input_artifact_ids = task_data.get("input_artifact_ids", [])
            parameters = task_data.get("parameters", {})
            
            # Get input text from artifacts
            input_text = await self._get_input_text(input_artifact_ids)
            if not input_text:
                raise ValueError("No input text found in artifacts")
            
            # Generate summary
            summary = await self._generate_summary(input_text, parameters)
            
            # Create output artifact
            output_artifact_id = await self.artifact_repo.create_artifact(
                source_agent_id=self.agent_id,
                workflow_id=uuid.UUID(workflow_id),
                task_id=uuid.UUID(task_id),
                content=summary,
                content_type="text/plain",
                parent_artifact_ids=[uuid.UUID(aid) for aid in input_artifact_ids],
                metadata={
                    "model_used": "gpt-3.5-turbo",
                    "input_length": len(input_text),
                    "output_length": len(summary),
                    "parameters": parameters
                }
            )
            
            return {
                "task_id": task_id,
                "workflow_id": workflow_id,
                "status": "completed",
                "output_artifact_ids": [str(output_artifact_id)],
                "processing_time_ms": 0,  # Will be calculated by caller
                "confidence_score": 0.85  # Mock confidence for Phase 0
            }
            
        except Exception as e:
            return {
                "task_id": task_data.get("task_id"),
                "workflow_id": task_data.get("workflow_id"),
                "status": "failed",
                "error_code": "PROCESSING_ERROR",
                "error_message": str(e)
            }
    
    async def _get_input_text(self, artifact_ids: list) -> str:
        """
        Retrieve input text from artifacts
        """
        for artifact_id in artifact_ids:
            artifact = await self.artifact_repo.get_artifact(uuid.UUID(artifact_id))
            if artifact and artifact["content_type"] == "text/plain":
                return artifact["content"]
        return ""
    
    async def _generate_summary(self, text: str, parameters: Dict[str, Any]) -> str:
        """
        Generate summary using OpenAI API or mock for Phase 0
        """
        max_length = parameters.get("max_length", 200)
        
        # For Phase 0 MVP, use a simple mock summarization
        # In production, this would call OpenAI API
        if settings.OPENAI_API_KEY:
            return await self._call_openai_api(text, max_length)
        else:
            return self._mock_summary(text, max_length)
    
    async def _call_openai_api(self, text: str, max_length: int) -> str:
        """
        Call OpenAI API for summarization
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are a text summarizer. Provide a concise summary of the given text in at most {max_length} characters."
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ],
                        "max_tokens": 150,
                        "temperature": 0.3
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"OpenAI API error: {response.status_code}")
                    
        except Exception as e:
            # Fallback to mock
            return self._mock_summary(text, max_length)
    
    def _mock_summary(self, text: str, max_length: int) -> str:
        """
        Mock summarization for development/testing
        """
        # Simple extractive summary - take first few sentences
        sentences = text.split('.')
        summary = '.'.join(sentences[:3]) + '.'
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary