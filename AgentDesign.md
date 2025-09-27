# Phase 0 - Agent Types and Capabilities Definition

## Agent Card Template

### Standard Agent Card Format
```yaml
agent_id: unique_identifier
name: Human-readable name
type: neural | symbolic | meta | external
version: semantic_version
capabilities:
  - primary_function_1
  - primary_function_2
deployment_options:
  api_providers:
    - provider_name: {models: [model_list]}
  local_options:
    - local_system: {models: [model_list]}
input_formats:
  - format_type: description
output_formats:
  - format_type: description
resource_requirements:
  api_mode:
    rate_limit: requests_per_hour
    max_execution_time: seconds
  local_mode:
    memory_mb: number
    cpu_cores: number
    max_execution_time: seconds
reliability_metrics:
  expected_success_rate: percentage
  retry_strategy: none | exponential_backoff | custom
  timeout_handling: fail | partial_output | retry
metadata:
  description: Brief description of agent purpose
  use_cases: [list of typical use cases]
  created_date: ISO_timestamp
  updated_date: ISO_timestamp
```

## MVP Agent Definitions (Phase 0 Subset)

### Neural Agent

#### Text Summarization Agent
```yaml
agent_id: neural_summarizer_v1
name: Text Summarization Agent
type: neural
version: 1.0.0
capabilities:
  - text_summarization
deployment_options:
  api_providers:
    - openai: {models: [gpt-3.5-turbo, gpt-4]}
  local_options:
    - ollama: {models: [llama2, mistral]}
input_formats:
  - text/plain: plain text documents
output_formats:
  - text/plain: summary text
resource_requirements:
  api_mode:
    rate_limit: 100_requests_per_hour
    max_execution_time: 30
  local_mode:
    memory_mb: 4096
    cpu_cores: 2
    max_execution_time: 60
reliability_metrics:
  expected_success_rate: 80%
  retry_strategy: exponential_backoff
  timeout_handling: partial_output
metadata:
  description: Generates concise summaries from text documents
  use_cases: [document_analysis, content_curation, research_synthesis]
  created_date: 2025-01-01T00:00:00Z
  updated_date: 2025-01-01T00:00:00Z
```

### Symbolic Agent

#### Logic Validation Agent
```yaml
agent_id: symbolic_validator_v1
name: Logic Validation Agent
type: symbolic
version: 1.0.0
capabilities:
  - schema_validation
  - consistency_checking
deployment_options:
  local_only:
    - python_engine: {dependencies: [validation_libraries]}
input_formats:
  - application/json: data to validate against schema
output_formats:
  - application/json: validation results with error details
resource_requirements:
  local_mode:
    memory_mb: 512
    cpu_cores: 1
    max_execution_time: 10
reliability_metrics:
  expected_success_rate: 98%
  retry_strategy: none
  timeout_handling: fail
metadata:
  description: Validates data and outputs against predefined schemas and rules
  use_cases: [quality_assurance, data_verification, output_validation]
  created_date: 2025-01-01T00:00:00Z
  updated_date: 2025-01-01T00:00:00Z
```

### Meta-Agent

#### Workflow Supervisor Agent
```yaml
agent_id: meta_supervisor_v1
name: Workflow Supervisor Agent
type: meta
version: 1.0.0
capabilities:
  - workflow_monitoring
  - task_routing
  - error_detection_and_recovery
  - output_quality_assessment
deployment_options:
  local_only:
    - orchestration_engine: {built_in: true}
input_formats:
  - application/json: workflow definitions and agent status
output_formats:
  - application/json: workflow status and routing decisions
resource_requirements:
  local_mode:
    memory_mb: 2048
    cpu_cores: 2
    max_execution_time: 5
reliability_metrics:
  expected_success_rate: 99%
  retry_strategy: custom
  timeout_handling: retry
metadata:
  description: Orchestrates workflow execution and ensures system reliability
  use_cases: [workflow_management, error_recovery, system_monitoring]
  created_date: 2025-01-01T00:00:00Z
  updated_date: 2025-01-01T00:00:00Z
```

## A2A Message Format

### Canonical Internal Message Structure
```json
{
  "task_id": "task_001",
  "workflow_id": "workflow_123", 
  "agent_id": "neural_summarizer_v1",
  "message_type": "task_request | task_response | status_update | error",
  "input_artifact_ids": ["artifact_456"],
  "output_artifact_ids": ["artifact_789"],
  "payload": {
    "text": "Document to summarize...",
    "parameters": {"max_length": 200}
  },
  "metadata": {
    "priority": "normal",
    "retry_count": 0,
    "timeout_seconds": 30
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "status": "pending | in_progress | completed | failed"
}
```

### Message Flow Examples

#### Task Request
```json
{
  "task_id": "task_001",
  "workflow_id": "doc_analysis_123",
  "agent_id": "neural_summarizer_v1",
  "message_type": "task_request",
  "input_artifact_ids": ["doc_456"],
  "payload": {
    "text": "Long document text here...",
    "parameters": {"summary_type": "executive"}
  },
  "metadata": {
    "priority": "normal",
    "timeout_seconds": 30
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "status": "pending"
}
```

#### Task Response
```json
{
  "task_id": "task_001",
  "workflow_id": "doc_analysis_123",
  "agent_id": "neural_summarizer_v1",
  "message_type": "task_response",
  "input_artifact_ids": ["doc_456"],
  "output_artifact_ids": ["summary_789"],
  "payload": {
    "summary": "Executive summary of the document...",
    "confidence_score": 0.85
  },
  "metadata": {
    "processing_time_ms": 15000,
    "model_used": "gpt-3.5-turbo"
  },
  "timestamp": "2025-01-01T12:00:30Z",
  "status": "completed"
}
```

## Initial Task-to-Agent Mapping

### Primary Workflows for Phase 0 Testing

1. **Document Analysis Pipeline**
   - Input: Text document → Neural Summarizer → Symbolic Validator → Meta Supervisor
   - Output: Validated summary with quality metrics

2. **Data Validation Pipeline**
   - Input: JSON or structured data → Symbolic Validator → Meta Supervisor
   - Output: Validated data with error/warning reports

### Agent Selection Logic
- **Neural agents**: Text generation, summarization, pattern recognition
- **Symbolic agents**: Validation, consistency checking, schema verification  
- **Meta agents**: Workflow coordination, error handling, task routing

### Workflow Coordination Details

#### Meta-Agent Task Queue Management
```python
# Pseudocode for meta-agent workflow coordination
class WorkflowCoordinator:
    def route_task(self, task):
        agent = self.select_agent_by_capability(task.requirements)
        if agent.is_available() and agent.health_status == 'healthy':
            return self.dispatch_task(agent, task)
        else:
            return self.queue_task_for_retry(task)
    
    def handle_agent_failure(self, task, error):
        if error.type == 'timeout':
            alternative_agent = self.find_backup_agent(task.requirements)
            return self.dispatch_task(alternative_agent, task)
        elif error.type == 'invalid_output':
            return self.retry_task_with_validation(task)
        else:
            return self.mark_workflow_failed(task.workflow_id, error)
```

## Agent Registry Schema

### Database Structure for Agent Tracking
```sql
CREATE TABLE agents (
    agent_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('neural', 'symbolic', 'meta', 'external'),
    version VARCHAR(20) NOT NULL,
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    capabilities JSON,
    deployment_options JSON,
    input_formats JSON,
    output_formats JSON,
    resource_requirements JSON,
    reliability_metrics JSON,
    metadata JSON,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE agent_instances (
    instance_id VARCHAR(50) PRIMARY KEY,
    agent_id VARCHAR(50) REFERENCES agents(agent_id),
    deployment_type ENUM('api', 'local'),
    endpoint_url VARCHAR(255),
    api_key_required BOOLEAN DEFAULT FALSE,
    current_load INTEGER DEFAULT 0,
    max_concurrent_tasks INTEGER DEFAULT 1,
    last_health_check TIMESTAMP,
    status ENUM('healthy', 'degraded', 'unhealthy') DEFAULT 'healthy'
);
```

## Configuration Management

### User Configuration for API vs Local
```yaml
# User's agent configuration file
neural_summarizer_v1:
  deployment_type: api
  provider: openai
  model: gpt-3.5-turbo
  api_key: ${OPENAI_API_KEY}

neural_extractor_v1:
  deployment_type: local
  provider: ollama
  model: llama2
  endpoint: http://localhost:11434

symbolic_validator_v1:
  deployment_type: local
  # Built-in symbolic agents run locally by default
```

## Validation and Testing Strategy

### Agent Capability Testing
- **Unit Tests**: Each agent handles expected input/output formats correctly
- **Integration Tests**: Agents communicate properly via A2A protocol
- **Configuration Tests**: Both API and local deployments work correctly
- **Reliability Tests**: Agents meet expected success rates under normal conditions

### Workflow Testing  
- **End-to-end Tests**: Complete workflows execute successfully with mixed deployment types
- **Error Handling Tests**: Meta-agent correctly handles agent failures and timeouts
- **Routing Tests**: Tasks are assigned to appropriate agents based on capabilities and availability

### Deployment Testing
- **API Integration**: Verify connections to OpenAI, Anthropic, Groq APIs
- **Local Model Testing**: Verify Ollama integration and OpenAI-compatible endpoints
- **Failover Testing**: System handles API rate limits and local model unavailability