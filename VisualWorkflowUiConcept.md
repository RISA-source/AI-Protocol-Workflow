# Phase 0 - Visual Workflow UI Concept

## Core UI Design Philosophy

### Primary Goals
- **Intuitive**: Non-technical users can create workflows visually
- **Powerful**: Advanced users can access JSON/YAML for complex configurations
- **Real-time**: Live workflow execution monitoring with status updates
- **Scalable**: Support simple 2-node workflows up to complex multi-step pipelines

### Design Approach
- **Node-based**: Agents are visual nodes, artifacts flow through edges
- **Drag-and-drop**: Agents from palette → canvas, auto-connection
- **Context-aware**: Smart suggestions based on agent capabilities and artifact types
- **Progressive disclosure**: Simple view by default, advanced options on demand

## Main UI Layout

### Application Structure
```
┌─────────────────────────────────────────────────────────────────┐
│  AI Orchestrator Platform                            [User] [⚙️] │
├─────────────────────────────────────────────────────────────────┤
│  📁 Workflows  │  🤖 Agents  │  📊 Artifacts  │  📈 Monitor    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────────────────────────────────┐  │
│  │             │  │                                         │  │
│  │   Agent     │  │                                         │  │
│  │  Palette    │  │          Workflow Canvas                │  │
│  │             │  │                                         │  │
│  │ 🧠 Neural   │  │                                         │  │
│  │ ⚡ Symbolic │  │                                         │  │
│  │ 👁️ Meta     │  │                                         │  │
│  │             │  │                                         │  │
│  └─────────────┘  └─────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Properties Panel / Live Execution Status                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Node Design Specifications

### Agent Node Visual Structure
```
┌──────────────────────┐
│ 🧠 Neural Summarizer │  ← Agent type icon + name
├──────────────────────┤
│ ●○○ Status Indicator │  ← Execution status (●=running, ○=pending)
├──────────────────────┤
│ 📄→📝 text/plain     │  ← Input/output format hints
├──────────────────────┤
│ ⚡ 45s ⚠️ 85%        │  ← Execution time & confidence (during/after run)
└──────────────────────┘
     ↑              ↑
   Input           Output
 Connection      Connection
   Point           Point
```

### Node States and Visual Indicators
```css
/* Node Status Colors */
.node-pending    { border: 2px solid #6b7280; background: #f9fafb; }
.node-running    { border: 2px solid #3b82f6; background: #dbeafe; animation: pulse; }
.node-completed  { border: 2px solid #10b981; background: #d1fae5; }
.node-failed     { border: 2px solid #ef4444; background: #fee2e2; }
.node-warning    { border: 2px solid #f59e0b; background: #fef3c7; }

/* Connection Points */
.connection-input  { border-radius: 50%; width: 12px; height: 12px; background: #6366f1; }
.connection-output { border-radius: 50%; width: 12px; height: 12px; background: #10b981; }
```

### Node Types and Icons
```yaml
node_types:
  neural:
    icon: "🧠"
    color: "#3b82f6"  # Blue
    examples: ["Summarizer", "Code Generator", "Data Extractor"]
  
  symbolic:
    icon: "⚡"
    color: "#8b5cf6"  # Purple
    examples: ["Validator", "Rule Engine", "Logic Checker"]
  
  meta:
    icon: "👁️"
    color: "#6b7280"  # Gray
    examples: ["Supervisor", "Router", "Monitor"]
  
  external:
    icon: "🌐"
    color: "#10b981"  # Green
    examples: ["API Connector", "Database Query", "File Reader"]
  
  user:
    icon: "👤"
    color: "#f59e0b"  # Amber
    examples: ["Input", "Manual Review", "Approval"]
```

## Agent Palette Design

### Collapsible Categories
```
┌─────────────────┐
│ 🔍 Search...    │  ← Filter agents by name/capability
├─────────────────┤
│ ▼ 🧠 Neural     │  ← Expandable categories
│   └ Summarizer  │
│   └ Code Gen    │
│   └ Extractor   │
├─────────────────┤
│ ▼ ⚡ Symbolic   │
│   └ Validator   │
│   └ Rule Engine │
├─────────────────┤
│ ▼ 👁️ Meta       │
│   └ Supervisor  │
├─────────────────┤
│ ▲ 🌐 External   │  ← Collapsed category
│ ▲ 👤 User       │
└─────────────────┘
```

### Agent Card in Palette
```
┌─────────────────┐
│ 🧠 Summarizer   │  ← Draggable agent card
├─────────────────┤
│ text → summary  │  ← Quick capability hint
│ ⚡ 60s avg      │  ← Performance indicator
│ 📊 85% success │  ← Reliability indicator
└─────────────────┘
```

## Workflow Canvas Interactions

### Drag and Drop Behavior
1. **Agent Placement**: Drag from palette → drop on canvas → auto-position with snap-to-grid
2. **Node Connection**: 
   - Hover output port → show connection preview
   - Drag from output → input port highlights compatible targets
   - Drop on compatible input → create edge
   - Drop on incompatible input → show error message
3. **Multi-selection**: Ctrl+click multiple nodes → group operations (move, delete)
4. **Canvas Navigation**: Pan (mouse drag), zoom (mouse wheel), fit-to-screen (hotkey)

### Connection Rules and Validation
```python
class ConnectionValidator:
    def can_connect(self, source_node, target_node) -> bool:
        """Validate if two nodes can be connected"""
        source_output_types = source_node.output_formats
        target_input_types = target_node.input_formats
        
        # Check format compatibility
        compatible_formats = set(source_output_types) & set(target_input_types)
        if not compatible_formats:
            return False
        
        # Prevent circular dependencies
        if self.would_create_cycle(source_node, target_node):
            return False
        
        # Check agent-specific rules
        return self.check_agent_compatibility(source_node.agent_type, target_node.agent_type)
    
    def get_connection_suggestions(self, source_node) -> List[str]:
        """Suggest compatible next agents"""
        suggestions = []
        for agent in self.available_agents:
            if self.can_connect(source_node, agent):
                suggestions.append(agent.name)
        return suggestions
```

### Edge Visualization and States
```
Workflow Edge States:
• Planned:     ┈┈┈┈┈→  (dashed gray line)
• Active:      ━━━━━→  (solid blue line, animated)  
• Completed:   ━━━━━→  (solid green line)
• Failed:      ┅┅┅┅→   (dotted red line)
• Artifact:    ═══▣═→  (thick line with artifact icon)
```

## Properties Panel Design

### Context-Sensitive Panel
```
┌────────────────────────────────────────┐
│ Properties: Neural Summarizer          │
├────────────────────────────────────────┤
│                                        │
│ ⚙️  Configuration                      │
│ ├ Max Length: [200] characters         │
│ ├ Summary Type: [Executive ▼]         │
│ └ Model: [gpt-3.5-turbo ▼]           │
│                                        │
│ 📊 Status & Metrics                   │
│ ├ Status: ●○○ Running (32s elapsed)   │
│ ├ Input: artifact_123 (received)      │
│ └ Output: artifact_456 (pending)      │
│                                        │
│ 📋 Agent Details                      │
│ ├ Version: 1.0.0                      │
│ ├ Deployment: API (OpenAI)            │
│ └ Success Rate: 85%                   │
│                                        │
│ 🔧 Advanced                           │
│ └ [View JSON Config] [Edit YAML]      │
└────────────────────────────────────────┘
```

### Live Execution Status Panel
```
┌────────────────────────────────────────┐
│ Workflow: Document Analysis            │
├────────────────────────────────────────┤
│                                        │
│ ⏳ Progress: Step 2/4 (50%)           │
│ ▓▓▓▓▓░░░░░                            │
│                                        │
│ 📊 Execution Timeline:                │
│ ✅ Input Received        00:00        │
│ ✅ Neural Summarizer     00:15        │
│ 🔄 Symbolic Validator    01:23        │ ← Currently running
│ ⏸️  Meta Supervisor      --:--        │ ← Pending
│                                        │
│ 📁 Artifacts Generated: 2              │
│ ├ Original Document (1.2KB)           │
│ └ Summary Text (0.3KB)                │
│                                        │
│ [⏸️ Pause] [⏹️ Stop] [🔄 Retry]        │
└────────────────────────────────────────┘
```

## Hierarchical Workflow Support

### Nested Workflow Design
```
Main Workflow Canvas:
┌─────────────────────────────────────────────────┐
│                                                 │
│  [Input] → [📊 Data Processing] → [Output]     │
│                      ↑                         │
│                 Double-click to                 │
│                 expand sub-workflow             │
└─────────────────────────────────────────────────┘

Sub-workflow Detail View:
┌─────────────────────────────────────────────────┐
│  📊 Data Processing (Sub-workflow)              │
│  ← Back to Main Workflow                        │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Extractor] → [Validator] → [Formatter]       │
│       ↓             ↓             ↓            │
│   [artifact1]   [artifact2]   [artifact3]      │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Workflow Grouping and Organization
```python
class WorkflowHierarchy:
    def create_sub_workflow(self, nodes: List[Node], name: str) -> SubWorkflow:
        """Group selected nodes into a collapsible sub-workflow"""
        sub_workflow = SubWorkflow(
            name=name,
            nodes=nodes,
            inputs=self.find_external_inputs(nodes),
            outputs=self.find_external_outputs(nodes)
        )
        return sub_workflow
    
    def collapse_sub_workflow(self, sub_workflow: SubWorkflow) -> CompositeNode:
        """Replace sub-workflow nodes with single composite node"""
        return CompositeNode(
            name=sub_workflow.name,
            internal_workflow=sub_workflow,
            input_ports=sub_workflow.inputs,
            output_ports=sub_workflow.outputs
        )
```

## Responsive Design and Mobile Considerations

### Desktop Layout (Primary Target)
- Full-featured interface with all panels visible
- Drag-and-drop with precise mouse interactions
- Multi-monitor support for large workflows
- Keyboard shortcuts for power users

### Tablet Layout (Secondary)
- Simplified palette (icons only, expandable)
- Touch-optimized node sizing and connection points
- Gesture support (pinch zoom, two-finger pan)
- Collapsible panels for more canvas space

### Mobile Layout (View Only)
- Workflow monitoring and status viewing
- No editing capabilities (too complex for small screens)
- Push notifications for workflow completion/errors
- Swipe navigation between workflow steps

## JSON/YAML Schema Access

### Advanced Configuration Modal
```
┌──────────────────────────────────────────────────┐
│ Advanced Configuration: Neural Summarizer        │
├──────────────────────────────────────────────────┤
│                                                  │
│ [Visual] [JSON] [YAML] ← Format tabs             │
│                                                  │
│ {                                                │
│   "agent_id": "neural_summarizer_v1",           │
│   "parameters": {                                │
│     "max_length": 200,                          │
│     "model": "gpt-3.5-turbo",                   │
│     "temperature": 0.7                          │
│   },                                             │
│   "timeout": 60,                                │
│   "retry_strategy": "exponential_backoff"       │
│ }                                                │
│                                                  │
│ [✓ Validate] [Apply] [Cancel]                   │
└──────────────────────────────────────────────────┘
```

### Workflow Export Format
```yaml
# Example workflow definition export
workflow:
  name: "Document Analysis Pipeline"
  version: "1.0"
  created_by: "user123"
  
nodes:
  - id: "input_1"
    type: "user_input"
    position: {x: 100, y: 100}
    
  - id: "summarizer_1"
    type: "neural_summarizer_v1"
    position: {x: 300, y: 100}
    config:
      max_length: 200
      model: "gpt-3.5-turbo"
      
  - id: "validator_1"
    type: "symbolic_validator_v1"
    position: {x: 500, y: 100}

connections:
  - from: "input_1"
    to: "summarizer_1"
    artifact_type: "text/plain"
    
  - from: "summarizer_1"
    to: "validator_1"  
    artifact_type: "text/plain"
```

## Implementation Technology Stack

### Frontend Framework: React + TypeScript
```typescript
// Core UI components
interface WorkflowNode {
  id: string;
  type: string;
  position: {x: number, y: number};
  data: {
    agent_id: string;
    config: Record<string, any>;
    status: 'pending' | 'running' | 'completed' | 'failed';
  };
}

interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  artifact_type: string;
  status: 'planned' | 'active' | 'completed' | 'failed';
}
```

### Canvas Library: React Flow
- Production-ready node-based editor
- Built-in drag-and-drop, zoom, pan
- Extensible node and edge types
- Performance optimized for large graphs

### Additional Libraries
- **State Management**: Zustand (lightweight, no boilerplate)
- **Forms**: React Hook Form (agent configuration)
- **UI Components**: Tailwind CSS + Headless UI
- **Real-time**: WebSocket connection for live updates
- **Code Editor**: Monaco Editor (for JSON/YAML editing)

## Phase 0 MVP Implementation Plan

### Week 1-2: Core Canvas
1. Basic React Flow setup with draggable nodes
2. Agent palette with 3 agent types (Neural, Symbolic, Meta)
3. Simple node connection with format validation
4. Properties panel showing selected node details

### Week 3-4: Workflow Execution
1. "Run Workflow" button triggers HTTP requests to agents
2. Live status updates via polling (WebSocket later)
3. Artifact visualization in properties panel
4. Basic error handling and retry UI

### Foundation for Phase 1
1. JSON/YAML configuration modal
2. Workflow save/load functionality
3. Sub-workflow grouping basics
4. Mobile-responsive layout adjustments

This UI design balances simplicity for Phase 0 with a clear architectural foundation for advanced features in later phases.