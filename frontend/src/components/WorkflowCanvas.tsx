import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { v4 as uuidv4 } from 'uuid';

import AgentPalette from './AgentPalette.tsx';
import PropertiesPanel from './PropertiesPanel.tsx';

// Import custom node types
import AgentNode from './nodes/AgentNode.tsx';

// Define custom node types
const nodeTypes = {
  agentNode: AgentNode,
};

// Initial nodes for Phase 0 demo
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'agentNode',
    position: { x: 250, y: 25 },
    data: {
      agentId: 'neural_summarizer_v1',
      name: 'Neural Summarizer',
      type: 'neural',
      status: 'pending'
    },
  },
  {
    id: '2',
    type: 'agentNode',
    position: { x: 250, y: 150 },
    data: {
      agentId: 'symbolic_validator_v1',
      name: 'Symbolic Validator',
      type: 'symbolic',
      status: 'pending'
    },
  },
];

const initialEdges: Edge[] = [];

const WorkflowCanvas: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const addNode = useCallback((agentData: any) => {
    const newNode: Node = {
      id: uuidv4(),
      type: 'agentNode',
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100
      },
      data: {
        agentId: agentData.agent_id,
        name: agentData.name,
        type: agentData.type,
        status: 'pending'
      },
    };
    setNodes((nds) => nds.concat(newNode));
  }, [setNodes]);

  const runWorkflow = useCallback(async () => {
    // Convert React Flow nodes/edges to workflow definition
    const workflowDefinition = {
      name: "Document Analysis Pipeline",
      steps: nodes.map((node, index) => ({
        step_id: index + 1,
        agent_id: node.data.agentId,
        input_artifact_ids: [], // Will be populated from edges
        parameters: {}
      }))
    };

    try {
      const response = await fetch('http://localhost:8000/api/v1/workflows/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowDefinition),
      });

      const result = await response.json();
      console.log('Workflow executed:', result);
    } catch (error) {
      console.error('Error running workflow:', error);
    }
  }, [nodes]);

  return (
    <div className="flex h-full w-full">
      {/* Agent Palette */}
      <div className="w-64 bg-gray-100 border-r border-gray-300">
        <AgentPalette onAddNode={addNode} />
        <div className="p-4">
          <button
            onClick={runWorkflow}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Run Workflow
          </button>
        </div>
      </div>

      {/* Workflow Canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant={"dots" as BackgroundVariant} gap={12} size={1} />
        </ReactFlow>
      </div>

      {/* Properties Panel */}
      <div className="w-80 bg-white border-l border-gray-300">
        <PropertiesPanel selectedNode={selectedNode} />
      </div>
    </div>
  );
};

export default WorkflowCanvas;