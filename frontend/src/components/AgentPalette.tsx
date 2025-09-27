import React, { useState, useEffect } from 'react';

interface Agent {
  agent_id: string;
  name: string;
  type: string;
  capabilities: string[];
  status: string;
  description?: string;
}

interface AgentPaletteProps {
  onAddNode: (agent: Agent) => void;
}

const AgentPalette: React.FC<AgentPaletteProps> = ({ onAddNode }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['neural', 'symbolic', 'meta']));

  useEffect(() => {
    // For Phase 0, use static agent data
    // In production, this would fetch from the backend
    const staticAgents: Agent[] = [
      {
        agent_id: 'neural_summarizer_v1',
        name: 'Neural Summarizer',
        type: 'neural',
        capabilities: ['text_summarization'],
        status: 'active',
        description: 'Generates concise summaries from text documents'
      },
      {
        agent_id: 'symbolic_validator_v1',
        name: 'Symbolic Validator',
        type: 'symbolic',
        capabilities: ['schema_validation', 'consistency_checking'],
        status: 'active',
        description: 'Validates data and outputs against predefined schemas and rules'
      },
      {
        agent_id: 'meta_supervisor_v1',
        name: 'Meta Supervisor',
        type: 'meta',
        capabilities: ['workflow_monitoring', 'task_routing'],
        status: 'active',
        description: 'Orchestrates workflow execution and ensures system reliability'
      }
    ];
    setAgents(staticAgents);
  }, []);

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.capabilities.some(cap => cap.toLowerCase().includes(searchTerm.toLowerCase())) ||
    agent.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const agentsByCategory = filteredAgents.reduce((acc, agent) => {
    if (!acc[agent.type]) acc[agent.type] = [];
    acc[agent.type].push(agent);
    return acc;
  }, {} as Record<string, Agent[]>);

  const getCategoryIcon = (type: string) => {
    switch (type) {
      case 'neural': return '🧠';
      case 'symbolic': return '⚡';
      case 'meta': return '👁️';
      default: return '🤖';
    }
  };

  const getCategoryColor = (type: string) => {
    switch (type) {
      case 'neural': return 'text-primary-600 bg-primary-50 border-primary-200';
      case 'symbolic': return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'meta': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'neural': return '🧠';
      case 'symbolic': return '⚡';
      case 'meta': return '👁️';
      default: return '🤖';
    }
  };

  const getAgentCardStyle = (type: string) => {
    switch (type) {
      case 'neural': return 'hover:bg-primary-100 border-primary-200';
      case 'symbolic': return 'hover:bg-purple-100 border-purple-200';
      case 'meta': return 'hover:bg-gray-100 border-gray-200';
      default: return 'hover:bg-gray-100 border-gray-200';
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-6 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-white">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">Agent Palette</h2>
            <p className="text-sm text-slate-500">Drag agents to build workflows</p>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search agents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white shadow-sm"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 018 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Agent Categories */}
      <div className="flex-1 overflow-y-auto px-4 py-2">
        {Object.entries(agentsByCategory).map(([category, categoryAgents]) => (
          <div key={category} className="mb-3">
            {/* Category Header */}
            <button
              onClick={() => toggleCategory(category)}
              className={`w-full flex items-center justify-between p-4 rounded-xl border transition-all duration-200 hover:shadow-md ${getCategoryColor(category)}`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-xl">{getCategoryIcon(category)}</span>
                <div className="text-left">
                  <span className="font-semibold text-sm capitalize text-slate-800">{category} Agents</span>
                  <div className="text-xs text-slate-500">{categoryAgents.length} available</div>
                </div>
              </div>
              <svg
                className={`w-5 h-5 text-slate-500 transition-transform duration-200 ${expandedCategories.has(category) ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Category Agents */}
            {expandedCategories.has(category) && (
              <div className="mt-2 space-y-2 ml-4">
                {categoryAgents.map((agent) => (
                  <div
                    key={agent.agent_id}
                    className={`p-4 border rounded-xl cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.02] ${getAgentCardStyle(agent.type)}`}
                    onClick={() => onAddNode(agent)}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${agent.type === 'neural' ? 'bg-blue-100' : agent.type === 'symbolic' ? 'bg-purple-100' : 'bg-slate-100'}`}>
                          <span className="text-2xl">{getAgentIcon(agent.type)}</span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <div className="font-semibold text-sm text-slate-800 truncate">{agent.name}</div>
                          <div className={`w-3 h-3 rounded-full flex-shrink-0 ${agent.status === 'active' ? 'bg-green-500' : 'bg-slate-400'}`}></div>
                        </div>
                        <div className="text-xs text-slate-500 font-mono truncate mb-2">{agent.agent_id}</div>
                        {agent.description && (
                          <div className="text-xs text-slate-600 mb-3 line-clamp-2 leading-relaxed">{agent.description}</div>
                        )}
                        <div className="flex flex-wrap gap-1">
                          {agent.capabilities.slice(0, 3).map((cap) => (
                            <span key={cap} className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-md font-medium">
                              {cap.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Empty state when no agents match search */}
        {Object.keys(agentsByCategory).length === 0 && searchTerm && (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-sm font-medium text-slate-600 mb-1">No agents found</h3>
            <p className="text-xs text-slate-500">Try adjusting your search terms</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentPalette;