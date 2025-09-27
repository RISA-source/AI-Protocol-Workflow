# Phase 0 - Artifact Repository Design

## Storage Backend Strategy

### Phase 0: Local Development (MVP)
**Primary Storage**: PostgreSQL for all artifact metadata and small content
**File Storage**: Local filesystem for binary/large artifacts
**Rationale**: Single dependency, easy to develop and debug locally

### Future Phases: Production Ready
**Structured Data**: PostgreSQL for metadata, relationships, and small text artifacts
**Binary Storage**: MinIO (S3-compatible) for large files, images, documents
**Caching**: Redis for frequently accessed artifacts (optional)

## Core Artifact Schema

### Primary Artifact Table
```sql
CREATE TABLE artifacts (
    -- Identity
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_artifact_ids UUID[] DEFAULT '{}',  -- Array of parent UUIDs for DAG
    version INTEGER DEFAULT 1,
    
    -- Provenance
    source_agent_id VARCHAR(50) NOT NULL,
    workflow_id UUID NOT NULL,
    task_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Content Classification
    content_type VARCHAR(100) NOT NULL,  -- MIME type or custom type
    content_category ENUM('text', 'code', 'data', 'image', 'document', 'binary') NOT NULL,
    size_bytes BIGINT DEFAULT 0,
    
    -- Storage Location
    storage_type ENUM('inline', 'filesystem', 's3') DEFAULT 'inline',
    storage_path VARCHAR(500),  -- File path or S3 key
    content_text TEXT,  -- Inline storage for small text artifacts
    
    -- Metadata
    title VARCHAR(200),
    description TEXT,
    tags VARCHAR(100)[] DEFAULT '{}',
    custom_metadata JSONB DEFAULT '{}',
    
    -- Quality & Validation
    validation_status ENUM('pending', 'valid', 'invalid', 'warning') DEFAULT 'pending',
    validation_details JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),  -- 0.00 to 1.00
    
    -- Indexing
    CONSTRAINT valid_version CHECK (version > 0),
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- Indexes for performance
CREATE INDEX idx_artifacts_workflow ON artifacts(workflow_id);
CREATE INDEX idx_artifacts_source_agent ON artifacts(source_agent_id);  
CREATE INDEX idx_artifacts_created_at ON artifacts(created_at);
CREATE INDEX idx_artifacts_parent_ids ON artifacts USING GIN(parent_artifact_ids);
CREATE INDEX idx_artifacts_tags ON artifacts USING GIN(tags);
CREATE INDEX idx_artifacts_content_type ON artifacts(content_type);
```

### Artifact Dependencies (DAG Tracking)
```sql
-- Explicit dependency tracking for complex relationships
CREATE TABLE artifact_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_artifact_id UUID NOT NULL REFERENCES artifacts(artifact_id) ON DELETE CASCADE,
    parent_artifact_id UUID NOT NULL REFERENCES artifacts(artifact_id) ON DELETE CASCADE,
    dependency_type ENUM('direct_input', 'reference', 'derived_from', 'validated_by') DEFAULT 'direct_input',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(child_artifact_id, parent_artifact_id, dependency_type)
);

CREATE INDEX idx_deps_child ON artifact_dependencies(child_artifact_id);
CREATE INDEX idx_deps_parent ON artifact_dependencies(parent_artifact_id);
```

### Workflow Context Table
```sql
CREATE TABLE workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('running', 'completed', 'failed', 'paused') DEFAULT 'running',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),  -- User ID or system identifier
    workflow_definition JSONB,  -- Store the original workflow steps
    
    -- Metrics
    total_steps INTEGER DEFAULT 0,
    completed_steps INTEGER DEFAULT 0,
    failed_steps INTEGER DEFAULT 0
);

CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created_at ON workflows(created_at);
```

## Artifact Operations API

### Core CRUD Operations
```python
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

class ArtifactRepository:
    
    def create_artifact(self, 
                       source_agent_id: str,
                       workflow_id: UUID,
                       task_id: UUID,
                       content: Any,
                       content_type: str,
                       parent_artifact_ids: List[UUID] = None,
                       metadata: Dict[str, Any] = None) -> UUID:
        """Create new artifact and return its ID"""
        
        artifact_id = uuid4()
        content_category = self._determine_category(content_type)
        storage_type, storage_path, content_text = self._prepare_storage(content, content_type)
        
        query = """
        INSERT INTO artifacts (
            artifact_id, parent_artifact_ids, source_agent_id, workflow_id, task_id,
            content_type, content_category, storage_type, storage_path, content_text,
            custom_metadata, size_bytes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        size_bytes = len(str(content).encode('utf-8')) if isinstance(content, str) else 0
        
        self.cursor.execute(query, (
            artifact_id, parent_artifact_ids or [], source_agent_id, workflow_id, task_id,
            content_type, content_category, storage_type, storage_path, content_text,
            json.dumps(metadata or {}), size_bytes
        ))
        
        # Create dependency relationships
        if parent_artifact_ids:
            self._create_dependencies(artifact_id, parent_artifact_ids, 'direct_input')
        
        self.connection.commit()
        return artifact_id
    
    def get_artifact(self, artifact_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve artifact by ID with content"""
        query = """
        SELECT artifact_id, parent_artifact_ids, source_agent_id, workflow_id, task_id,
               content_type, content_category, storage_type, storage_path, content_text,
               title, description, tags, custom_metadata, validation_status, 
               confidence_score, created_at, version, size_bytes
        FROM artifacts WHERE artifact_id = %s
        """
        
        self.cursor.execute(query, (artifact_id,))
        row = self.cursor.fetchone()
        
        if not row:
            return None
        
        artifact = dict(zip([col[0] for col in self.cursor.description], row))
        
        # Load content based on storage type
        if artifact['storage_type'] == 'inline':
            artifact['content'] = artifact['content_text']
        elif artifact['storage_type'] == 'filesystem':
            artifact['content'] = self._load_from_file(artifact['storage_path'])
        elif artifact['storage_type'] == 's3':
            artifact['content'] = self._load_from_s3(artifact['storage_path'])
        
        return artifact
    
    def get_lineage(self, artifact_id: UUID, direction: str = 'both') -> Dict[str, List[UUID]]:
        """Get artifact lineage - parents (inputs) and/or children (outputs)"""
        lineage = {'parents': [], 'children': []}
        
        if direction in ['both', 'parents']:
            # Get parent artifacts (what this artifact was derived from)
            query = """
            SELECT parent_artifact_id, dependency_type 
            FROM artifact_dependencies 
            WHERE child_artifact_id = %s
            """
            self.cursor.execute(query, (artifact_id,))
            lineage['parents'] = [{'id': row[0], 'type': row[1]} for row in self.cursor.fetchall()]
        
        if direction in ['both', 'children']:
            # Get child artifacts (what was derived from this artifact)
            query = """
            SELECT child_artifact_id, dependency_type 
            FROM artifact_dependencies 
            WHERE parent_artifact_id = %s
            """
            self.cursor.execute(query, (artifact_id,))
            lineage['children'] = [{'id': row[0], 'type': row[1]} for row in self.cursor.fetchall()]
        
        return lineage
    
    def get_workflow_artifacts(self, workflow_id: UUID, 
                             order_by: str = 'created_at') -> List[Dict[str, Any]]:
        """Get all artifacts for a workflow, ordered by creation time or other field"""
        query = f"""
        SELECT artifact_id, source_agent_id, content_type, content_category,
               title, description, validation_status, created_at, size_bytes
        FROM artifacts 
        WHERE workflow_id = %s 
        ORDER BY {order_by}
        """
        
        self.cursor.execute(query, (workflow_id,))
        return [dict(zip([col[0] for col in self.cursor.description], row)) 
                for row in self.cursor.fetchall()]
```

### Storage Strategy Implementation
```python
def _prepare_storage(self, content: Any, content_type: str) -> tuple:
    """Determine how and where to store artifact content"""
    
    # Inline storage for small text content
    if content_type.startswith('text/') and len(str(content)) < 10000:  # < 10KB
        return 'inline', None, str(content)
    
    # Filesystem storage for development
    if content_type.startswith('text/') or content_type == 'application/json':
        file_path = self._save_to_file(content, content_type)
        return 'filesystem', file_path, None
    
    # Binary content always goes to filesystem (or S3 in production)
    file_path = self._save_binary_to_file(content, content_type)
    return 'filesystem', file_path, None

def _save_to_file(self, content: Any, content_type: str) -> str:
    """Save content to local filesystem"""
    import os
    from datetime import datetime
    
    # Create directory structure: artifacts/YYYY/MM/DD/
    today = datetime.now()
    dir_path = f"artifacts/{today.year:04d}/{today.month:02d}/{today.day:02d}"
    os.makedirs(dir_path, exist_ok=True)
    
    # Generate filename
    artifact_uuid = str(uuid4())
    extension = self._get_file_extension(content_type)
    file_path = f"{dir_path}/{artifact_uuid}{extension}"
    
    # Write content
    if isinstance(content, str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        with open(file_path, 'wb') as f:
            f.write(content)
    
    return file_path
```

## DAG-based Lineage Tracking

### Lineage Query Examples
```sql
-- Get all ancestors of an artifact (recursive)
WITH RECURSIVE artifact_ancestors AS (
    -- Base case: direct parents
    SELECT parent_artifact_id as ancestor_id, child_artifact_id as descendant_id, 
           dependency_type, 1 as depth
    FROM artifact_dependencies
    WHERE child_artifact_id = $1  -- Target artifact ID
    
    UNION ALL
    
    -- Recursive case: parents of parents
    SELECT ad.parent_artifact_id, aa.descendant_id, 
           ad.dependency_type, aa.depth + 1
    FROM artifact_dependencies ad
    JOIN artifact_ancestors aa ON ad.child_artifact_id = aa.ancestor_id
    WHERE aa.depth < 10  -- Prevent infinite recursion
)
SELECT a.artifact_id, a.title, a.content_type, a.source_agent_id, 
       aa.dependency_type, aa.depth
FROM artifact_ancestors aa
JOIN artifacts a ON aa.ancestor_id = a.artifact_id
ORDER BY aa.depth;

-- Get workflow artifact flow (DAG visualization data)
SELECT 
    a1.artifact_id as source_id,
    a1.title as source_title,
    a1.source_agent_id as source_agent,
    a2.artifact_id as target_id,
    a2.title as target_title,
    a2.source_agent_id as target_agent,
    ad.dependency_type
FROM artifact_dependencies ad
JOIN artifacts a1 ON ad.parent_artifact_id = a1.artifact_id
JOIN artifacts a2 ON ad.child_artifact_id = a2.artifact_id
WHERE a1.workflow_id = $1 AND a2.workflow_id = $1
ORDER BY a1.created_at, a2.created_at;
```

### Artifact Versioning Strategy
```python
def create_artifact_version(self, original_artifact_id: UUID, 
                          new_content: Any, 
                          source_agent_id: str,
                          changes_description: str = None) -> UUID:
    """Create a new version of an existing artifact"""
    
    # Get original artifact info
    original = self.get_artifact(original_artifact_id)
    if not original:
        raise ValueError(f"Original artifact {original_artifact_id} not found")
    
    # Create new version with incremented version number
    new_version = original['version'] + 1
    
    # Create new artifact record
    new_artifact_id = self.create_artifact(
        source_agent_id=source_agent_id,
        workflow_id=original['workflow_id'],
        task_id=uuid4(),  # New task ID for versioning operation
        content=new_content,
        content_type=original['content_type'],
        parent_artifact_ids=[original_artifact_id],  # Original as parent
        metadata={
            'version_of': str(original_artifact_id),
            'version_number': new_version,
            'changes_description': changes_description,
            'original_metadata': original.get('custom_metadata', {})
        }
    )
    
    # Update version number
    self.cursor.execute(
        "UPDATE artifacts SET version = %s WHERE artifact_id = %s",
        (new_version, new_artifact_id)
    )
    self.connection.commit()
    
    return new_artifact_id
```

## API Endpoints for Phase 0

### RESTful Artifact API
```python
# FastAPI implementation
from fastapi import FastAPI, HTTPException
from uuid import UUID
from typing import List, Optional

app = FastAPI()

@app.post("/api/v1/artifacts", response_model=dict)
def create_artifact(request: ArtifactCreateRequest):
    """Create new artifact"""
    try:
        artifact_id = repository.create_artifact(
            source_agent_id=request.source_agent_id,
            workflow_id=request.workflow_id,
            task_id=request.task_id,
            content=request.content,
            content_type=request.content_type,
            parent_artifact_ids=request.parent_artifact_ids,
            metadata=request.metadata
        )
        return {"artifact_id": artifact_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/artifacts/{artifact_id}")
def get_artifact(artifact_id: UUID):
    """Retrieve artifact by ID"""
    artifact = repository.get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact

@app.get("/api/v1/artifacts/{artifact_id}/lineage")
def get_artifact_lineage(artifact_id: UUID, direction: str = "both"):
    """Get artifact lineage (parents and children)"""
    lineage = repository.get_lineage(artifact_id, direction)
    return lineage

@app.get("/api/v1/workflows/{workflow_id}/artifacts")
def get_workflow_artifacts(workflow_id: UUID):
    """Get all artifacts for a workflow"""
    artifacts = repository.get_workflow_artifacts(workflow_id)
    return {"artifacts": artifacts}

@app.put("/api/v1/artifacts/{artifact_id}/validate")
def validate_artifact(artifact_id: UUID, validation: ArtifactValidation):
    """Update artifact validation status"""
    repository.update_validation_status(
        artifact_id, 
        validation.status, 
        validation.details
    )
    return {"status": "updated"}
```

## Sample Data and Testing

### Test Artifact Creation Flow
```python
def test_artifact_flow():
    """Test complete artifact creation and lineage tracking"""
    repo = ArtifactRepository()
    
    # Create workflow
    workflow_id = repo.create_workflow("Document Analysis Test", "Phase 0 testing")
    
    # Step 1: Original document artifact
    doc_id = repo.create_artifact(
        source_agent_id="user_input",
        workflow_id=workflow_id,
        task_id=uuid4(),
        content="This is a long document that needs to be summarized...",
        content_type="text/plain",
        metadata={"source": "user_upload", "length": 1500}
    )
    
    # Step 2: Summary artifact (child of document)
    summary_id = repo.create_artifact(
        source_agent_id="neural_summarizer_v1",
        workflow_id=workflow_id,
        task_id=uuid4(),
        content="Summary: The document discusses important topics...",
        content_type="text/plain",
        parent_artifact_ids=[doc_id],
        metadata={"model_used": "gpt-3.5-turbo", "confidence": 0.85}
    )
    
    # Step 3: Validation artifact (child of summary)
    validation_id = repo.create_artifact(
        source_agent_id="symbolic_validator_v1",
        workflow_id=workflow_id,
        task_id=uuid4(),
        content={"is_valid": True, "issues": [], "score": 0.92},
        content_type="application/json",
        parent_artifact_ids=[summary_id],
        metadata={"validation_rules": ["length_check", "coherence_check"]}
    )
    
    # Test lineage queries
    summary_lineage = repo.get_lineage(summary_id)
    print(f"Summary parents: {summary_lineage['parents']}")
    print(f"Summary children: {summary_lineage['children']}")
    
    # Test workflow artifacts
    workflow_artifacts = repo.get_workflow_artifacts(workflow_id)
    print(f"Workflow has {len(workflow_artifacts)} artifacts")
    
    return workflow_id, [doc_id, summary_id, validation_id]
```

### Local Development Setup
```sql
-- Initialize local PostgreSQL database
CREATE DATABASE ai_orchestrator_dev;

-- Run schema creation scripts
\i artifacts_schema.sql

-- Insert sample agent registrations
INSERT INTO agents (agent_id, name, type, status) VALUES
('neural_summarizer_v1', 'Text Summarization Agent', 'neural', 'active'),
('symbolic_validator_v1', 'Logic Validation Agent', 'symbolic', 'active'),
('meta_supervisor_v1', 'Workflow Supervisor', 'meta', 'active');
```

### Configuration for Phase 0
```yaml
# config/database.yml
database:
  host: localhost
  port: 5432
  database: ai_orchestrator_dev
  username: postgres
  password: ${DB_PASSWORD}
  
storage:
  type: filesystem
  base_path: ./artifacts
  max_inline_size: 10240  # 10KB
  
artifact_retention:
  keep_versions: 10
  cleanup_after_days: 90
```

This design provides a solid foundation for artifact management with proper lineage tracking, flexible storage options, and a clear migration path from local development to production infrastructure.

One technical note:
The _prepare_storage method assumes text content can be measured with len(str(content)), but for binary content you might want to handle bytes differently. Consider adding type checking there.
Minor enhancement suggestion:
Consider adding a checksum field to detect content corruption:
sqlcontent_checksum VARCHAR(64),  -- SHA-256 hash for integrity checking