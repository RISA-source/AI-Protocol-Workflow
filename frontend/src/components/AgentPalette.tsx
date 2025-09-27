import React, { useState, useEffect } from 'react';

interface Agent {
  agent_id: string;
  name: string;
  type: string;
  capabilities: string[];
  status: string;
}

interface AgentPaletteProps {
  onAddNode: (agent: Agent) => void;
}

const AgentPalette: React.FC<AgentPaletteProps> = ({ onAddNode }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // For Phase 0, use static agent data
    // In production, this would fetch from the backend
    const staticAgents: Agent[] = [
      {
        agent_id: 'neural_summarizer_v1',
        name: 'Neural Summarizer',
        type: 'neural',
        capabilities: ['text_summarization'],
        status: 'active'
      },
      {
        agent_id: 'symbolic_validator_v1',
        name: 'Symbolic Validator',
        type: 'symbolic',
        capabilities: ['schema_validation', 'consistency_checking'],
        status: 'active'
      },
      {
        agent_id: 'meta_supervisor_v1',
        name: 'Meta Supervisor',
        type: 'meta',
        capabilities: ['workflow_monitoring', 'task_routing'],
        status: 'active'
      }
    ];
    setAgents(staticAgents);
  }, []);

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.capabilities.some(cap => cap.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'neural': return '🧠';
      case 'symbolic': return '⚡';
      case 'meta': return '👁️';
      default: return '🤖';
    }
  };

  const getAgentColor = (type: string) => {
    switch (type) {
      case 'neural': return 'bg-blue-50 border-blue-200';
      case 'symbolic': return 'bg-purple-50 border-purple-200';
      case 'meta': return 'bg-gray-50 border-gray-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Agent Palette</h2>

      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search agents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Agent List */}
      <div className="space-y-2">
        {filteredAgents.map((agent) => (
          <div
            key={agent.agent_id}
            className={`p-3 border rounded-md cursor-pointer hover:shadow-md transition-shadow ${getAgentColor(agent.type)}`}
            onClick={() => onAddNode(agent)}
          >
            <div className="flex items-center space-x-2">
              <span className="text-xl">{getAgentIcon(agent.type)}</span>
              <div className="flex-1">
                <div className="font-medium text-sm">{agent.name}</div>
                <div className="text-xs text-gray-600">{agent.agent_id}</div>
              </div>
              <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            </div>
            <div className="mt-2">
              <div className="text-xs text-gray-500">
                Capabilities: {agent.capabilities.join(', ')}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentPalette;