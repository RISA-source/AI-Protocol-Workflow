# Phase 0 - Protocol & Communication Strategy

## MVP Messaging Mechanism

### Primary Transport: HTTP Only
**Rationale**: Maximum simplicity for Phase 0, widely supported, easy to debug

#### HTTP Endpoints for A2A Communication
```
POST   /api/v1/tasks                    # Create new task
GET    /api/v1/tasks/{task_id}          # Get task status
PUT    /api/v1/tasks/{task_id}/status   # Update task status (agents report progress)
POST   /api/v1/tasks/{task_id}/complete # Mark task complete with output
GET    /api/v1/workflows/{workflow_id}  # Get workflow status
POST   /api/v1/artifacts               # Store artifact
GET    /api/v1/artifacts/{artifact_id}  # Retrieve artifact
```

#### Authentication
- **Method**: JWT tokens with agent-specific scopes
- **Content-Type**: `application/json` for all communications
- **Headers**: `Authorization: Bearer {jwt_token}`

## A2A Protocol Specification (Simplified)

### Canonical Message Format
```json
{
  "task_id": "task_001",
  "workflow_id": "workflow_123",
  "source_agent": "meta_supervisor_v1",
  "target_agent": "neural_summarizer_v1",
  "message_type": "request|response|error",
  "payload": {
    "operation": "summarize_text",
    "input_data": "Document content here...",
    "parameters": {"max_length": 200},
    "input_artifact_ids": ["artifact_456"]
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "status": "pending|in_progress|completed|failed"
}
```

### Message Types and Flows

#### 1. Task Request (Agent Generates Artifact IDs)
```json
{
  "task_id": "task_001",
  "workflow_id": "doc_analysis_123",
  "source_agent": "meta_supervisor_v1",
  "target_agent": "neural_summarizer_v1",
  "message_type": "request",
  "payload": {
    "operation": "summarize_text",
    "input_artifact_ids": ["doc_456"],
    "parameters": {"max_length": 200}
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "status": "pending"
}
```

#### 2. Task Response (Success with Generated Artifact IDs)
```json
{
  "task_id": "task_001",
  "workflow_id": "doc_analysis_123",
  "source_agent": "neural_summarizer_v1",
  "target_agent": "meta_supervisor_v1",
  "message_type": "response",
  "payload": {
    "output_artifact_ids": ["summary_789"],
    "processing_time_ms": 15000
  },
  "timestamp": "2025-01-01T12:00:15Z",
  "status": "completed"
}
```

#### 3. Error Response
```json
{
  "task_id": "task_001",
  "workflow_id": "doc_analysis_123",
  "source_agent": "neural_summarizer_v1",
  "target_agent": "meta_supervisor_v1",
  "message_type": "error",
  "payload": {
    "error_code": "TIMEOUT_EXCEEDED",
    "error_message": "Task execution exceeded timeout",
    "partial_output_artifact_ids": []
  },
  "timestamp": "2025-01-01T12:01:00Z",
  "status": "failed"
}
```

## Timeout, Retry, and Error Handling

### Simple Timeout Configuration
```python
TIMEOUTS = {
    'neural_agents': {
        'api_mode': 60,      # seconds
        'local_mode': 120    # seconds
    },
    'symbolic_agents': {
        'local_mode': 30     # seconds
    },
    'meta_agents': {
        'coordination': 5    # seconds
    }
}
```

### Basic Retry Strategy
```python
class SimpleRetryStrategy:
    MAX_RETRIES = 2
    RETRY_DELAY = 5  # seconds, fixed delay
    
    def should_retry(self, error_type: str, retry_count: int) -> bool:
        retryable_errors = ['timeout', 'network_error', 'api_rate_limit']
        return (error_type in retryable_errors and 
                retry_count < self.MAX_RETRIES)
    
    def get_delay(self, retry_count: int) -> int:
        return self.RETRY_DELAY
```

### Error Classification
```python
ERROR_TYPES = {
    'timeout': {'retryable': True, 'max_retries': 2},
    'network_error': {'retryable': True, 'max_retries': 2},
    'api_rate_limit': {'retryable': True, 'max_retries': 3},
    'invalid_input': {'retryable': False, 'max_retries': 0},
    'agent_offline': {'retryable': True, 'max_retries': 1}
}
```

## Protocol Adapter Layer (Foundation Only)

### Simple Adapter Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ProtocolAdapter(ABC):
    """Simplified adapter interface for future protocol support"""
    
    @abstractmethod
    def name(self) -> str:
        """Return protocol name (e.g., 'a2a', 'openai')"""
        pass
    
    @abstractmethod
    def send_message(self, target_agent: str, message: Dict[str, Any]) -> bool:
        """Send message to target agent, return success status"""
        pass
    
    @abstractmethod
    def translate_to_internal(self, external_message: Dict[str, Any]) -> Dict[str, Any]:
        """Convert external protocol message to internal A2A format"""
        pass
    
    @abstractmethod
    def translate_from_internal(self, internal_message: Dict[str, Any]) -> Dict[str, Any]:
        """Convert internal A2A message to external protocol format"""
        pass
```

### A2A Native Adapter (Reference Implementation)
```python
class A2AAdapter(ProtocolAdapter):
    def __init__(self, endpoint: str, auth_token: str):
        self.endpoint = endpoint
        self.auth_token = auth_token
    
    def name(self) -> str:
        return "a2a-1.0"
    
    def send_message(self, target_agent: str, message: Dict[str, Any]) -> bool:
        try:
            response = requests.post(
                f"{self.endpoint}/api/v1/tasks",
                json=message,
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def translate_to_internal(self, external_message: Dict[str, Any]) -> Dict[str, Any]:
        # A2A is our native format, no translation needed
        return external_message
    
    def translate_from_internal(self, internal_message: Dict[str, Any]) -> Dict[str, Any]:
        # A2A is our native format, no translation needed
        return internal_message
```

## Communication Flow Examples

### Basic Task Execution Flow
```
1. Meta-Agent creates task: POST /api/v1/tasks
2. Meta-Agent assigns to Neural Agent: PUT /api/v1/tasks/{id}/status
3. Neural Agent processes task and creates artifacts
4. Neural Agent completes: POST /api/v1/tasks/{id}/complete (with artifact IDs)
5. Meta-Agent checks status: GET /api/v1/tasks/{id}
6. Meta-Agent routes to next agent (Symbolic Validator) with new artifact IDs
7. Workflow continues until complete
```

### Artifact ID Generation Flow
```
1. Meta-agent creates task → POST /tasks (no output artifact IDs specified)
2. Neural agent receives request
3. Neural agent processes input and generates output
4. Neural agent creates artifact(s) → assigns UUIDs 
5. Neural agent stores artifacts → POST /api/v1/artifacts
6. Neural agent marks task complete → POST /tasks/{id}/complete, returning artifact ID(s)
7. Meta-agent updates workflow with actual artifact references for next step
```

### Error Handling Flow
```
1. Meta-Agent sends task to Neural Agent
2. Neural Agent times out after 60 seconds
3. Meta-Agent detects timeout via status polling
4. Meta-Agent retries task (attempt 2/3)
5. If retry fails, Meta-Agent marks workflow as failed
6. Error details stored in workflow status
```

### Status Polling Strategy
```python
class StatusPoller:
    POLL_INTERVAL = 2  # seconds
    
    def poll_task_status(self, task_id: str) -> Dict[str, Any]:
        """Simple polling mechanism for task status"""
        while True:
            response = requests.get(f"/api/v1/tasks/{task_id}")
            task_status = response.json()
            
            if task_status['status'] in ['completed', 'failed']:
                return task_status
            
            time.sleep(self.POLL_INTERVAL)
```

## Implementation Priorities for Phase 0

### Immediate (Week 1-2)
1. HTTP endpoints for task creation and status
2. Basic A2A message format validation
3. Simple timeout detection (polling-based)
4. Basic error responses

### Short-term (Week 3-4)
1. JWT authentication for agents
2. Artifact storage and retrieval endpoints
3. Simple retry logic with fixed delays
4. Agent registration and discovery

### Foundation for Phase 1
1. Protocol adapter interface (empty implementations)
2. Structured error classification
3. Basic workflow status tracking
4. Simple agent health checking

## Testing Strategy for Phase 0

### Protocol Testing
- **Message Format**: JSON schema validation for A2A messages
- **HTTP Transport**: Basic request/response functionality
- **Timeout Handling**: Simulate slow agents, verify timeout detection
- **Error Handling**: Test common failure modes (network, timeout, invalid input)

### Integration Testing
- **Agent Communication**: Meta-agent successfully dispatches to neural/symbolic agents
- **Workflow Execution**: End-to-end document analysis pipeline
- **Error Recovery**: Failed task properly retried and eventually marked failed
- **Artifact Flow**: Artifacts correctly stored and retrieved between agents

### Load Testing (Minimal)
- **Sequential Workflows**: Process 10 documents sequentially without errors
- **Agent Availability**: Handle agent unavailability gracefully
- **Memory Usage**: Ensure artifact storage doesn't leak memory

## Configuration for Phase 0

### Agent Endpoints Configuration
```yaml
agents:
  neural_summarizer_v1:
    endpoint: "http://localhost:8001"
    timeout: 60
    max_retries: 2
  
  symbolic_validator_v1:
    endpoint: "http://localhost:8002"
    timeout: 30
    max_retries: 1
  
  meta_supervisor_v1:
    endpoint: "http://localhost:8000"  # Built-in orchestrator
    timeout: 5
    max_retries: 0
```

### System Configuration
```yaml
orchestrator:
  poll_interval: 2  # seconds
  max_concurrent_workflows: 5
  artifact_storage: "local_filesystem"  # Start simple
  log_level: "DEBUG"

authentication:
  jwt_secret: "${JWT_SECRET}"
  token_expiry: 3600  # 1 hour
```

This simplified version focuses on the core functionality needed for Phase 0 while maintaining the architectural foundation for future expansion. The complexity has been reduced significantly while keeping the essential A2A protocol structure and adapter pattern for future protocol support.