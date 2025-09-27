#!/usr/bin/env python3
"""
Test script for Phase 0 MVP - Document Analysis Pipeline
Demonstrates end-to-end workflow execution with A2A protocol
"""

import asyncio
import uuid
import sys
import traceback
from pathlib import Path

from sqlalchemy import text

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.meta_supervisor import MetaSupervisorAgent
from app.repositories.artifact_repository import ArtifactRepository
from app.core.database import init_db, AsyncSession, engine


async def ensure_workflow_and_task(session, workflow_name="Document Analysis Pipeline"):
    """Create workflow and a dummy task, return IDs"""
    workflow_id = uuid.uuid4()
    task_id = uuid.uuid4()

    # Insert workflow
    await session.execute(
        text("""
        INSERT INTO workflows (workflow_id, name, description, status, total_steps, completed_steps, failed_steps)
        VALUES (:workflow_id, :name, :desc, 'RUNNING', 2, 0, 0)
        """),
        {"workflow_id": workflow_id, "name": workflow_name, "desc": "Phase 0 MVP workflow"}
    )

    # Insert dummy task for workflow
    await session.execute(
        text("""
        INSERT INTO tasks (task_id, workflow_id, agent_id, status)
        VALUES (:task_id, :workflow_id, 'user_input', 'PENDING')
        """),
        {"task_id": task_id, "workflow_id": workflow_id}
    )

    await session.commit()
    return workflow_id, task_id


async def test_document_analysis_pipeline():
    print(" Starting Phase 0 MVP Test - Document Analysis Pipeline")
    print("=" * 60)

    # Step 0: Initialize DB
    print("  Step 0: Initializing database tables...")
    await init_db()
    print(" Database ready")

    # Initialize supervisor
    supervisor = MetaSupervisorAgent()

    async with AsyncSession(engine) as session:
        artifact_repo = ArtifactRepository()  # no session injection

        # Sample document
        document_text = """
        Artificial Intelligence (AI) is revolutionizing industries across the globe.
        Machine learning algorithms can now process vast amounts of data to identify
        patterns and make predictions. Natural language processing enables computers
        to understand and generate human-like text. Computer vision systems can
        recognize objects, faces, and scenes with remarkable accuracy.

        The field of AI encompasses various subdomains including neural networks,
        expert systems, robotics, and cognitive computing. Recent advances in deep
        learning have led to breakthroughs in areas such as image recognition,
        speech synthesis, and autonomous vehicles.

        While AI presents tremendous opportunities, it also raises important ethical
        considerations around privacy, bias, and job displacement. Responsible AI
        development requires careful attention to these challenges.
        """

        # Step 1: Create input document artifact (without workflow/task for now)
        print(" Step 1: Creating input document artifact...")
        try:
            # Create a temporary workflow for the input artifact
            temp_workflow_id = uuid.uuid4()
            temp_task_id = uuid.uuid4()
            await session.execute(
                text("""
                INSERT INTO workflows (workflow_id, name, description, status, total_steps, completed_steps, failed_steps)
                VALUES (:workflow_id, 'Input Preparation', 'Creating input artifact', 'COMPLETED', 1, 1, 0)
                """),
                {"workflow_id": temp_workflow_id}
            )
            await session.execute(
                text("""
                INSERT INTO tasks (task_id, workflow_id, agent_id, status)
                VALUES (:task_id, :workflow_id, 'user_input', 'COMPLETED')
                """),
                {"task_id": temp_task_id, "workflow_id": temp_workflow_id}
            )
            await session.commit()

            doc_artifact_id = await artifact_repo.create_artifact(
                source_agent_id="user_input",
                workflow_id=temp_workflow_id,
                task_id=temp_task_id,
                content=document_text,
                content_type="text/plain",
                metadata={
                    "source": "test_document",
                    "length": len(document_text),
                    "title": "AI Overview Document"
                }
            )
            print(f" Created document artifact: {doc_artifact_id}")
        except Exception:
            print(" Failed to create input document artifact")
            traceback.print_exc()
            return False

        # Step 2: Define workflow
        print("\n Step 2: Defining workflow...")
        workflow_definition = {
            "name": "Document Analysis Pipeline",
            "description": "Phase 0 MVP - Summarize and validate document",
            "steps": [
                {
                    "step_id": 1,
                    "agent_id": "neural_summarizer_v1",
                    "input_artifact_ids": [str(doc_artifact_id)],
                    "parameters": {"max_length": 200}
                },
                {
                    "step_id": 2,
                    "agent_id": "symbolic_validator_v1",
                    "input_artifact_ids": [],  # Will be populated from step 1 output
                    "parameters": {"rules": ["basic_schema_check", "length_check"]}
                }
            ]
        }

        # Step 4: Execute workflow with detailed error logging
        print(" Step 3: Executing workflow with meta-agent supervision...")
        try:
            result = await supervisor.execute_workflow(workflow_definition)
        except Exception as e:
            print(" Exception during workflow execution:")
            traceback.print_exc()
            return False

        print(f" Workflow Status: {result['status']}")
        print(f" Artifacts Generated: {result['artifacts_generated']}")

        # Step 5: Verify results
        print("\n Step 4: Verifying results...")
        if result['status'] == 'completed':
            try:
                # Use the workflow_id from the result
                result_workflow_id = uuid.UUID(result['workflow_id'])
                workflow_artifacts = await artifact_repo.get_workflow_artifacts(result_workflow_id)
                print(f" Total artifacts in workflow: {len(workflow_artifacts)}")

                for artifact in workflow_artifacts:
                    print(f"  • {artifact['title'] or 'Untitled'} ({artifact['content_type']}, {artifact['size_bytes']} bytes)")

                # Test lineage
                print("\n Step 5: Testing artifact lineage...")
                if workflow_artifacts:
                    last_artifact_id = workflow_artifacts[-1]['artifact_id']
                    lineage = await artifact_repo.get_lineage(uuid.UUID(last_artifact_id))
                    print(f" Lineage for {last_artifact_id}:")
                    print(f"   Parents: {len(lineage['parents'])}")
                    print(f"   Children: {len(lineage['children'])}")
            except Exception:
                print(" Failed verifying results")
                traceback.print_exc()
                return False
        else:
            print(" Workflow failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    print("\n Phase 0 MVP Test COMPLETED SUCCESSFULLY!")
    return True


async def main():
    try:
        success = await test_document_analysis_pipeline()
        if success:
            print("\n ALL TESTS PASSED - Phase 0 MVP is ready!")
        else:
            print("\n TESTS FAILED - Check implementation")
            sys.exit(1)
    except Exception as e:
        print(f"\n TEST ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
