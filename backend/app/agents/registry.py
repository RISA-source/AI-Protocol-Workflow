"""
Agent registry for managing available agents
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry for managing agent definitions and instances
    """
    
    def __init__(self):
        self.agents = {}
        self._load_default_agents()
    
    def _load_default_agents(self):
        """Load default agent definitions"""
        self.agents = {
            "neural_summarizer_v1": {
                "agent_id": "neural_summarizer_v1",
                "name": "Text Summarization Agent",
                "type": "neural",
                "version": "1.0.0",
                "capabilities": ["text_summarization"],
                "deployment_options": {
                    "api_providers": [{"openai": {"models": ["gpt-3.5-turbo", "gpt-4"]}}],
                    "local_options": [{"ollama": {"models": ["llama2", "mistral"]}}]
                },
                "input_formats": ["text/plain"],
                "output_formats": ["text/plain"],
                "resource_requirements": {
                    "api_mode": {
                        "rate_limit": 100,
                        "max_execution_time": 30
                    },
                    "local_mode": {
                        "memory_mb": 4096,
                        "cpu_cores": 2,
                        "max_execution_time": 60
                    }
                },
                "reliability_metrics": {
                    "expected_success_rate": 80,
                    "retry_strategy": "exponential_backoff",
                    "timeout_handling": "partial_output"
                },
                "metadata": {
                    "description": "Generates concise summaries from text documents",
                    "use_cases": ["document_analysis", "content_curation", "research_synthesis"]
                }
            },
            "symbolic_validator_v1": {
                "agent_id": "symbolic_validator_v1",
                "name": "Logic Validation Agent",
                "type": "symbolic",
                "version": "1.0.0",
                "capabilities": ["schema_validation", "consistency_checking"],
                "deployment_options": {
                    "local_only": [{"python_engine": {"dependencies": ["validation_libraries"]}}]
                },
                "input_formats": ["application/json", "text/plain"],
                "output_formats": ["application/json"],
                "resource_requirements": {
                    "local_mode": {
                        "memory_mb": 512,
                        "cpu_cores": 1,
                        "max_execution_time": 10
                    }
                },
                "reliability_metrics": {
                    "expected_success_rate": 98,
                    "retry_strategy": "none",
                    "timeout_handling": "fail"
                },
                "metadata": {
                    "description": "Validates data and outputs against predefined schemas and rules",
                    "use_cases": ["quality_assurance", "data_verification", "output_validation"]
                }
            },
            "meta_supervisor_v1": {
                "agent_id": "meta_supervisor_v1",
                "name": "Workflow Supervisor Agent",
                "type": "meta",
                "version": "1.0.0",
                "capabilities": ["workflow_monitoring", "task_routing", "error_detection_and_recovery", "output_quality_assessment"],
                "deployment_options": {
                    "local_only": [{"orchestration_engine": {"built_in": True}}]
                },
                "input_formats": ["application/json"],
                "output_formats": ["application/json"],
                "resource_requirements": {
                    "local_mode": {
                        "memory_mb": 2048,
                        "cpu_cores": 2,
                        "max_execution_time": 5
                    }
                },
                "reliability_metrics": {
                    "expected_success_rate": 99,
                    "retry_strategy": "custom",
                    "timeout_handling": "retry"
                },
                "metadata": {
                    "description": "Orchestrates workflow execution and ensures system reliability",
                    "use_cases": ["workflow_management", "error_recovery", "system_monitoring"]
                }
            }
        }
    
    async def register_default_agents(self):
        """Register default agents (placeholder for database storage)"""
        logger.info(f"Registered {len(self.agents)} default agents")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent definition by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return list(self.agents.values())
    
    def get_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Get agents that have a specific capability"""
        return [agent for agent in self.agents.values() if capability in agent["capabilities"]]