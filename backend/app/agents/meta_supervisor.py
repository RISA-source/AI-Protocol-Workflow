"""
Meta-Agent Supervisor - Phase 0 MVP implementation
"""

import uuid
from typing import Dict, Any, List

from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.models.workflows import WorkflowStatus, TaskStatus
from app.agents.neural_summarizer import NeuralSummarizerAgent
from app.agents.symbolic_validator import SymbolicValidatorAgent

class MetaSupervisorAgent:
    """
    Meta-agent that orchestrates workflow execution with supervision
    """
    
    def __init__(self):
        self.agent_id = "meta_supervisor_v1"
        self.endpoint = "http://localhost:8000"  # Built-in orchestrator
        self.artifact_repo = ArtifactRepository()
        self.workflow_repo = WorkflowRepository()

        # Agent instances (for Phase 0, direct instantiation)
        self.agent_instances = {
            "neural_summarizer_v1": NeuralSummarizerAgent(),
            "symbolic_validator_v1": SymbolicValidatorAgent()
        }
    
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow with supervision
        """
        try:
            # Create workflow record
            workflow_id = await self.workflow_repo.create_workflow(
                name=workflow_definition.get("name", "Unnamed Workflow"),
                description=workflow_definition.get("description", ""),
                workflow_definition=workflow_definition,
                total_steps=len(workflow_definition.get("steps", []))
            )

            # Execute steps with supervision
            results = []
            completed_steps = 0
            failed_steps = 0
            previous_outputs = {}  # Store outputs from previous steps

            for step in workflow_definition.get("steps", []):
                # Populate input_artifact_ids if empty and depends on previous steps
                if not step.get("input_artifact_ids"):
                    # For Phase 0, assume sequential and take from previous step
                    if results:
                        step["input_artifact_ids"] = results[-1].get("output_artifact_ids", [])

                result = await self._execute_step_with_supervision(step, workflow_id)
                results.append(result)

                if result["status"] == "completed":
                    completed_steps += 1
                    # Store outputs for potential use by next steps
                    previous_outputs[step["step_id"]] = result.get("output_artifact_ids", [])
                else:
                    failed_steps += 1
                    break  # Stop on first failure

            # Update workflow status
            final_status = WorkflowStatus.COMPLETED if failed_steps == 0 else WorkflowStatus.FAILED
            await self.workflow_repo.update_workflow_status(workflow_id, final_status, completed_steps, failed_steps)

            return {
                "workflow_id": str(workflow_id),
                "status": final_status.value,
                "results": results,
                "artifacts_generated": len(await self.artifact_repo.get_workflow_artifacts(workflow_id))
            }

        except Exception as e:
            # If workflow_id was created, update status
            if 'workflow_id' in locals():
                await self.workflow_repo.update_workflow_status(workflow_id, WorkflowStatus.FAILED)
            return {
                "workflow_id": str(workflow_id) if 'workflow_id' in locals() else None,
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_step_with_supervision(self, step: Dict[str, Any], workflow_id: uuid.UUID) -> Dict[str, Any]:
        """
        Execute single workflow step with supervision
        """
        agent_id = step.get("agent_id")

        # Create task in DB
        task_id = await self.workflow_repo.create_task(
            workflow_id=workflow_id,
            agent_id=agent_id,
            input_artifact_ids=step.get("input_artifact_ids", []),
            parameters=step.get("parameters", {})
        )

        # Update task status to in_progress
        await self.workflow_repo.update_task_status(task_id, TaskStatus.IN_PROGRESS)

        # Execute with retry logic
        max_retries = step.get("max_retries", 2)
        for attempt in range(max_retries + 1):
            try:
                result = await self._dispatch_task(agent_id, {
                    "task_id": str(task_id),
                    "workflow_id": str(workflow_id),
                    "agent_id": agent_id,
                    "input_artifact_ids": step.get("input_artifact_ids", []),
                    "parameters": step.get("parameters", {})
                })

                # Basic validation
                if self._is_valid_result(result, step):
                    # Update task as completed
                    await self.workflow_repo.update_task_status(task_id, TaskStatus.COMPLETED, result.get("output_artifact_ids", []))
                    return result
                else:
                    if attempt < max_retries:
                        continue  # Retry
                    else:
                        await self.workflow_repo.update_task_status(task_id, TaskStatus.FAILED, error_message="Validation failed after retries")
                        return {
                            "task_id": str(task_id),
                            "status": "failed",
                            "error": "Validation failed after retries"
                        }

            except Exception as e:
                if attempt == max_retries:
                    await self.workflow_repo.update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))
                    return {
                        "task_id": str(task_id),
                        "status": "failed",
                        "error": str(e)
                    }

        return {
            "task_id": str(task_id),
            "status": "failed",
            "error": "All attempts failed"
        }
    
    async def _dispatch_task(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch task to agent instance directly
        """
        agent = self.agent_instances.get(agent_id)
        if not agent:
            raise ValueError(f"No agent instance found for agent {agent_id}")

        return await agent.process_task(task_data)
    
    def _is_valid_result(self, result: Dict[str, Any], step: Dict[str, Any]) -> bool:
        """
        Basic result validation
        """
        if result.get("status") != "completed":
            return False

        # Check if output artifacts were created
        output_artifact_ids = result.get("output_artifact_ids", [])
        if not output_artifact_ids:
            return False

        # Basic size/content checks
        expected_output_type = step.get("expected_output_type", "text/plain")
        # For Phase 0, just check that we have some output
        return True