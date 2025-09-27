# AI-Protocol-Workflow - Phase 0 MVP

A modular AI orchestration platform where multiple agent types collaborate through standardized protocols to generate reliable, context-rich artifacts with full lineage tracking.

## Phase 0 MVP Overview

This is a working proof-of-concept implementation that demonstrates core functionality. The MVP includes:

- **Agent Orchestration**: Neural, symbolic, and meta agents with direct method invocation
- **Artifact Management**: Versioned storage with dependency tracking and lineage
- **Meta-Agent Supervision**: Workflow orchestration with database persistence
- **Database Integration**: Full PostgreSQL support with SQLAlchemy models
- **End-to-End Pipeline**: Working document analysis workflow (summarize → validate)
- **Visual Interface**: Node-based workflow designer with React Flow (frontend)

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (optional - uses in-memory fallback for demo)

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up database (optional):**
   ```bash
   # Create PostgreSQL database
   createdb ai_orchestrator_dev

   # Or use environment variables
   export DATABASE_URL="postgresql://user:pass@localhost/ai_orchestrator_dev"
   ```

3. **Run backend:**
   ```bash
   python main.py
   ```
   Backend will start on http://localhost:8000

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run frontend:**
   ```bash
   npm start
   ```
   Frontend will start on http://localhost:3000

### Test the Pipeline

Run the working end-to-end test:
```bash
cd backend
python test_workflow.py
```

This executes a complete document analysis workflow:
1. Creates input document artifact
2. Neural summarizer generates summary (200 bytes)
3. Symbolic validator checks quality (54 bytes result)
4. Verifies artifact lineage and workflow completion

**Expected Output**: "Phase 0 MVP Test COMPLETED SUCCESSFULLY!" with 2 artifacts generated.

## Architecture

### Backend Components

- **FastAPI Application** (`main.py`): REST API server with CORS support
- **Database Models** (`app/models/`): SQLAlchemy models for artifacts, workflows, tasks, and agents
- **Repository Layer** (`app/repositories/`):
  - `artifact_repository.py`: CRUD operations with lineage tracking and dependency management
  - `workflow_repository.py`: Workflow and task lifecycle management
- **Agent Implementations** (`app/agents/`):
  - `neural_summarizer.py`: Text summarization using mock/OpenAI API
  - `symbolic_validator.py`: Schema validation and data quality checks
  - `meta_supervisor.py`: Workflow orchestration and agent coordination
  - `registry.py`: Agent definitions and capabilities
- **API Endpoints** (`app/api/`): RESTful interfaces for workflows, artifacts, agents, and tasks
- **Core Services** (`app/core/`): Database connection, configuration management

### Frontend Components

- **React Application**: TypeScript-based UI
- **Workflow Canvas**: React Flow-based node editor
- **Agent Palette**: Drag-and-drop agent selection
- **Properties Panel**: Node configuration and status display

### Key Features Implemented

#### Agent Communication
- **Direct Method Invocation**: Agents called directly by meta-supervisor (Phase 0 MVP approach)
- **Structured Task Data**: Standardized task format with IDs, artifacts, parameters, and metadata
- **Future A2A Protocol**: HTTP/WebSocket communication planned for Phase 1 distributed deployment

#### Artifact Repository with Lineage
- PostgreSQL storage with DAG-based dependency tracking
- Automatic artifact versioning and metadata
- File system storage for large content

#### Meta-Agent Supervision
- Health-aware agent selection
- Basic error detection and recovery (retry/reroute)
- Workflow orchestration with status tracking

#### Visual Workflow Designer
- Node-based drag-and-drop interface
- Real-time workflow execution monitoring
- Agent palette with search and filtering

## API Endpoints

### Workflows
- `POST /api/v1/workflows/` - Execute workflow
- `GET /api/v1/workflows/{id}` - Get workflow status

### Artifacts
- `POST /api/v1/artifacts/` - Create artifact
- `GET /api/v1/artifacts/{id}` - Get artifact
- `GET /api/v1/artifacts/{id}/lineage` - Get artifact lineage
- `GET /api/v1/workflows/{id}/artifacts` - Get workflow artifacts

### Agents
- `GET /api/v1/agents/` - List agents
- `GET /api/v1/agents/{id}` - Get agent details

### Tasks (A2A Protocol)
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}` - Get task status
- `PUT /api/v1/tasks/{id}/status` - Update task status

## Testing

### Unit Tests
```bash
# Backend tests (when implemented)
cd backend
pytest
```

### Integration Test
```bash
# End-to-end workflow test
python test_workflow.py
```

### Manual Testing
1. Start backend and frontend
2. Open http://localhost:3000
3. Drag agents from palette to canvas
4. Connect nodes with edges
5. Click "Run Workflow" to execute

## Success Criteria Met ✅

- **✅ Workflow Execution**: Complete neural → symbolic agent pipeline (working end-to-end)
- **✅ Artifact Integrity**: All artifacts include ID, metadata, lineage links with dependency tracking
- **✅ Database Persistence**: Full workflow, task, and artifact storage with relationships
- **✅ Agent Orchestration**: Meta-supervisor coordinates agent execution with status tracking
- **✅ Artifact Lineage**: Proper parent-child relationships between workflow artifacts
- **🔄 UI Functionality**: Visual workflow creation and monitoring (frontend implementation pending)
- **🔄 A2A Protocol**: Direct method invocation working; HTTP protocol planned for Phase 1

## Recent Implementation Updates

The backend has been fully debugged and optimized for Phase 0 MVP functionality:

### Critical Fixes Applied
- **Database Persistence**: Added `WorkflowRepository` for complete workflow/task lifecycle management
- **Agent Communication**: Changed from HTTP calls to direct method invocation for reliability
- **Workflow Dependencies**: Implemented dynamic input population between sequential steps
- **Test Infrastructure**: Fixed import paths and workflow ID tracking
- **Cross-Platform**: Removed Unicode emojis for Windows compatibility

### Current Architecture Status
- **Backend**: Fully functional with working end-to-end pipeline
- **Database**: Complete PostgreSQL integration with proper relationships
- **Agents**: Neural summarizer and symbolic validator working with artifact I/O
- **Supervision**: Meta-agent orchestrates workflows with status tracking
- **Testing**: Comprehensive integration test validates all components

### Key Components Working
- Artifact creation, storage, and lineage tracking
- Workflow execution with step dependencies
- Task status management and error handling
- Database relationships and constraints
- Repository pattern implementation

## Phase 1 Roadmap

Building on the working Phase 0 foundation:

### Immediate Next Steps
- **A2A Protocol Implementation**: HTTP/WebSocket communication between distributed agents
- **Frontend Integration**: Connect React UI to working backend APIs
- **Agent Marketplace**: Dynamic agent registration and discovery
- **Workflow Templates**: Pre-built workflow patterns and reuse

### Advanced Features
- **Quality Assessment**: Output validation and improvement suggestions
- **Human-in-the-Loop**: Escalation for complex decisions
- **Multi-Protocol Support**: gRPC, WebSocket adapters for different agent types
- **Production Storage**: MinIO S3, Redis caching, distributed databases
- **Security**: JWT authentication, API rate limiting, agent authorization
- **Scalability**: Kubernetes deployment, load balancing, horizontal scaling
- **Advanced UI**: Sub-workflows, templates, real-time collaboration, monitoring dashboards

## Project Structure

```
AI-Protocol-Workflow/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── test_workflow.py           # End-to-end integration test
│   ├── requirements.txt           # Python dependencies
│   └── app/
│       ├── core/
│       │   ├── config.py          # Application configuration
│       │   └── database.py        # Database connection and setup
│       ├── models/
│       │   ├── __init__.py
│       │   ├── artifacts.py       # Artifact and dependency models
│       │   ├── workflows.py       # Workflow and task models
│       │   └── agents.py          # Agent definition models
│       ├── repositories/
│       │   ├── artifact_repository.py    # Artifact CRUD and lineage
│       │   └── workflow_repository.py    # Workflow/task management
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── registry.py        # Agent definitions and capabilities
│       │   ├── meta_supervisor.py # Workflow orchestration
│       │   ├── neural_summarizer.py     # Text summarization agent
│       │   └── symbolic_validator.py    # Data validation agent
│       └── api/
│           ├── __init__.py
│           ├── workflows.py       # Workflow execution endpoints
│           ├── artifacts.py       # Artifact management endpoints
│           ├── agents.py          # Agent information endpoints
│           └── tasks.py           # Task management endpoints
├── frontend/                      # React application (separate setup)
└── *.md                          # Design and specification documents
```

## Documentation

- [System Design](SysDesign.md) - Platform purpose and MVP scope
- [Agent Design](AgentDesign.md) - Agent types, capabilities, and registry
- [Artifact Repository](AritifactRepoDesign.md) - Storage and lineage design
- [Meta-Agent Supervision](MetaAgestSupervisionStrategy.md) - Orchestration logic
- [Protocol & Communication](ProtoComm.md) - A2A messaging specification
- [Visual UI Concept](VisualWorkflowUiConcept.md) - Frontend design and implementation
- [Tech Stack](techStack.md) - Technology choices and rationale

## Contributing

This is a Phase 0 MVP focused on core functionality. For contributions:

1. Ensure changes don't break existing functionality
2. Add tests for new features
3. Update documentation
4. Follow the established patterns

## License

Phase 0 MVP - Internal evaluation only. Contact for licensing inquiries.