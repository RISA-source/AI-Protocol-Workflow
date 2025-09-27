"""
Symbolic Validator Agent - Phase 0 MVP implementation
"""

import uuid
import json
from typing import Dict, Any, Optional
import jsonschema

from app.repositories.artifact_repository import ArtifactRepository

class SymbolicValidatorAgent:
    """
    Data validation agent using schema validation and basic checks
    """
    
    def __init__(self):
        self.agent_id = "symbolic_validator_v1"
        self.endpoint = "http://localhost:8002"  # Self-hosted endpoint for this agent
        self.artifact_repo = ArtifactRepository()
        
        # Basic validation schemas
        self.schemas = {
            "summary_schema": {
                "type": "string",
                "minLength": 10,
                "maxLength": 1000
            },
            "validation_result_schema": {
                "type": "object",
                "properties": {
                    "is_valid": {"type": "boolean"},
                    "issues": {"type": "array"},
                    "score": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["is_valid", "issues", "score"]
            }
        }
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a validation task
        """
        try:
            # Extract input data
            task_id = task_data.get("task_id")
            workflow_id = task_data.get("workflow_id")
            input_artifact_ids = task_data.get("input_artifact_ids", [])
            parameters = task_data.get("parameters", {})
            
            # Get input data from artifacts
            input_data = await self._get_input_data(input_artifact_ids)
            if not input_data:
                raise ValueError("No input data found in artifacts")
            
            # Perform validation
            validation_result = await self._validate_data(input_data, parameters)
            
            # Create output artifact
            output_artifact_id = await self.artifact_repo.create_artifact(
                source_agent_id=self.agent_id,
                workflow_id=uuid.UUID(workflow_id),
                task_id=uuid.UUID(task_id),
                content=json.dumps(validation_result, indent=2),
                content_type="application/json",
                parent_artifact_ids=[uuid.UUID(aid) for aid in input_artifact_ids],
                metadata={
                    "validation_rules": parameters.get("rules", ["basic_schema_check"]),
                    "input_count": len(input_artifact_ids),
                    "validation_score": validation_result["score"]
                }
            )
            
            return {
                "task_id": task_id,
                "workflow_id": workflow_id,
                "status": "completed",
                "output_artifact_ids": [str(output_artifact_id)],
                "processing_time_ms": 0,  # Will be calculated by caller
                "confidence_score": validation_result["score"]
            }
            
        except Exception as e:
            return {
                "task_id": task_data.get("task_id"),
                "workflow_id": task_data.get("workflow_id"),
                "status": "failed",
                "error_code": "VALIDATION_ERROR",
                "error_message": str(e)
            }
    
    async def _get_input_data(self, artifact_ids: list) -> Any:
        """
        Retrieve input data from artifacts
        """
        for artifact_id in artifact_ids:
            artifact = await self.artifact_repo.get_artifact(uuid.UUID(artifact_id))
            if artifact:
                if artifact["content_type"] == "application/json":
                    try:
                        return json.loads(artifact["content"])
                    except:
                        return artifact["content"]
                elif artifact["content_type"] == "text/plain":
                    return artifact["content"]
        return None
    
    async def _validate_data(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform validation checks on the data
        """
        validation_rules = parameters.get("rules", ["basic_schema_check"])
        issues = []
        score = 1.0
        
        # Apply validation rules
        for rule in validation_rules:
            if rule == "basic_schema_check":
                schema_result = self._validate_basic_schema(data)
                if not schema_result["valid"]:
                    issues.extend(schema_result["issues"])
                    score *= 0.8
            
            elif rule == "length_check":
                length_result = self._validate_length(data)
                if not length_result["valid"]:
                    issues.extend(length_result["issues"])
                    score *= 0.9
            
            elif rule == "coherence_check":
                coherence_result = self._validate_coherence(data)
                if not coherence_result["valid"]:
                    issues.extend(coherence_result["issues"])
                    score *= 0.95
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "score": max(0.0, score)
        }
    
    def _validate_basic_schema(self, data: Any) -> Dict[str, Any]:
        """
        Basic schema validation
        """
        issues = []
        
        # For text data, check if it's a reasonable string
        if isinstance(data, str):
            if len(data.strip()) == 0:
                issues.append("Empty or whitespace-only text")
            elif len(data) < 10:
                issues.append("Text too short (minimum 10 characters)")
        
        # For JSON data, check basic structure
        elif isinstance(data, dict):
            if len(data) == 0:
                issues.append("Empty JSON object")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _validate_length(self, data: Any) -> Dict[str, Any]:
        """
        Check data length constraints
        """
        issues = []
        
        if isinstance(data, str):
            if len(data) > 10000:
                issues.append("Text too long (maximum 10000 characters)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _validate_coherence(self, data: Any) -> Dict[str, Any]:
        """
        Basic coherence checks
        """
        issues = []
        
        if isinstance(data, str):
            # Check for excessive repetition
            words = data.lower().split()
            if len(words) > 10:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                max_repetitions = max(word_counts.values())
                if max_repetitions > len(words) * 0.3:  # More than 30% of words are repeats
                    issues.append("Excessive word repetition detected")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }