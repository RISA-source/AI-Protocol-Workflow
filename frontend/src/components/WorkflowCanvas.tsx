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

// Start with empty canvas for better UX
const initialNodes: Node[] = [];

const initialEdges: Edge[] = [];

const WorkflowCanvas: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [executionLog, setExecutionLog] = useState<string[]>([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({
      ...params,
      type: 'smoothstep',
      style: { stroke: '#64748b', strokeWidth: 2 }
    }, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const addNode = useCallback((agentData: any, position?: { x: number; y: number }) => {
    const nodeCount = nodes.length;
    const newNode: Node = {
      id: uuidv4(),
      type: 'agentNode',
      position: position || {
        x: 100 + (nodeCount * 50), // Stagger nodes horizontally
        y: 100 + (nodeCount * 80)  // Stagger nodes vertically
      },
      data: {
        agentId: agentData.agent_id,
        name: agentData.name,
        type: agentData.type,
        status: 'pending'
      },
    };
    setNodes((nds) => nds.concat(newNode));
  }, [nodes.length, setNodes]);

  const updateNodeStatus = useCallback((nodeId: string, status: string, additionalData?: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              status,
              ...additionalData
            }
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  const runWorkflow = useCallback(async () => {
    if (isRunning) return;

    setIsRunning(true);
    setExecutionLog([]);
    setWorkflowStatus(null);

    // Reset all nodes to pending
    nodes.forEach(node => updateNodeStatus(node.id, 'pending'));

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
      setExecutionLog(prev => [...prev, '🚀 Starting workflow execution...']);

      const response = await fetch('http://localhost:8000/api/v1/workflows/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowDefinition),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setExecutionLog(prev => [...prev, '✅ Workflow submitted successfully']);

      // Simulate real-time status updates (in real implementation, use WebSocket)
      setTimeout(() => {
        updateNodeStatus('1', 'running');
        setExecutionLog(prev => [...prev, '🧠 Neural Summarizer: Processing...']);
      }, 1000);

      setTimeout(() => {
        updateNodeStatus('1', 'completed', { executionTime: '2.3s', confidence: 0.85 });
        setExecutionLog(prev => [...prev, '✅ Neural Summarizer: Completed (85% confidence)']);
      }, 3000);

      setTimeout(() => {
        updateNodeStatus('2', 'running');
        setExecutionLog(prev => [...prev, '⚡ Symbolic Validator: Processing...']);
      }, 3500);

      setTimeout(() => {
        updateNodeStatus('2', 'completed', { executionTime: '1.1s', confidence: 0.92 });
        setExecutionLog(prev => [...prev, '✅ Symbolic Validator: Completed (92% confidence)']);
        setExecutionLog(prev => [...prev, '🎉 Workflow completed successfully!']);
        setIsRunning(false);
      }, 5000);

      console.log('Workflow executed:', result);
    } catch (error) {
      console.error('Error running workflow:', error);
      setExecutionLog(prev => [...prev, `❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`]);
      nodes.forEach(node => updateNodeStatus(node.id, 'failed'));
      setIsRunning(false);
    }
  }, [nodes, isRunning, updateNodeStatus]);

  return (
    <div className="flex h-full w-full bg-slate-50">
      {/* Agent Palette */}
      <div className="w-80 bg-white border-r border-slate-200 shadow-sm flex flex-col">
        <AgentPalette onAddNode={addNode} />

        {/* Run Workflow Button */}
        <div className="p-6 border-t border-slate-200 bg-slate-50">
          <button
            onClick={runWorkflow}
            disabled={isRunning || nodes.length === 0}
            className={`w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 ${
              isRunning || nodes.length === 0
                ? 'bg-slate-300 cursor-not-allowed text-slate-500'
                : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg transform hover:scale-[1.02]'
            }`}
          >
            {isRunning ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Running Workflow...</span>
              </div>
            ) : nodes.length === 0 ? (
              'Add agents to run workflow'
            ) : (
              '▶️ Run Workflow'
            )}
          </button>

          {/* Execution Log */}
          {executionLog.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Execution Log
              </h4>
              <div className="bg-white rounded-lg border border-slate-200 p-3 max-h-48 overflow-y-auto shadow-sm">
                <div className="space-y-2 text-sm">
                  {executionLog.map((log, index) => (
                    <div key={index} className="text-slate-600 font-mono text-xs leading-relaxed">{log}</div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Workflow Canvas - Main Area */}
      <div className="flex-1 relative bg-white">
        {nodes.length === 0 ? (
          /* Empty State */
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
            <div className="text-center max-w-md mx-auto p-8">
              <div className="w-24 h-24 mx-auto mb-6 bg-slate-200 rounded-full flex items-center justify-center">
                <svg className="w-12 h-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-700 mb-2">Start Building Your Workflow</h3>
              <p className="text-slate-500 mb-6">Drag agents from the palette to create your AI orchestration pipeline</p>
              <div className="flex items-center justify-center space-x-2 text-sm text-slate-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
                </svg>
                <span>← Drag agents here</span>
              </div>
            </div>
          </div>
        ) : (
          /* Canvas with nodes */
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            className="bg-slate-50"
            defaultViewport={{ x: 0, y: 0, zoom: 1 }}
            minZoom={0.1}
            maxZoom={2}
          >
            <Controls
              className="bg-white border border-slate-200 shadow-lg rounded-lg overflow-hidden"
              showZoom={true}
              showFitView={true}
              showInteractive={false}
            />
            <MiniMap
              className="bg-white border border-slate-200 shadow-lg rounded-lg"
              nodeColor={(node) => {
                switch (node.data?.type) {
                  case 'neural': return '#3b82f6';
                  case 'symbolic': return '#8b5cf6';
                  case 'meta': return '#6b7280';
                  default: return '#94a3b8';
                }
              }}
              nodeStrokeWidth={2}
              zoomable
              pannable
            />
            <Background
              variant={"dots" as BackgroundVariant}
              gap={24}
              size={1.5}
              color="#cbd5e1"
              className="opacity-30"
            />
          </ReactFlow>
        )}

        {/* Workflow Status Overlay */}
        {isRunning && (
          <div className="absolute top-6 right-6 bg-white rounded-xl shadow-xl border border-slate-200 p-4 z-10">
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
              <div>
                <div className="text-sm font-semibold text-slate-800">Workflow Running</div>
                <div className="text-xs text-slate-500">Processing agents...</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Properties Panel */}
      <div className="w-96 bg-white border-l border-slate-200 shadow-sm">
        <PropertiesPanel selectedNode={selectedNode} workflowStatus={workflowStatus} />
      </div>
    </div>
  );
};

export default WorkflowCanvas;