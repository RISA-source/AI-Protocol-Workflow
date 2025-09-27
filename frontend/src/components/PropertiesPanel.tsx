import React, { useState, useEffect } from 'react';
import { Node } from 'reactflow';

interface PropertiesPanelProps {
  selectedNode: Node | null;
  workflowStatus?: any;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ selectedNode, workflowStatus }) => {
  const [config, setConfig] = useState({
    maxLength: 200,
    model: 'gpt-3.5-turbo',
    temperature: 0.7
  });

  useEffect(() => {
    if (selectedNode?.data?.config) {
      setConfig(prev => ({ ...prev, ...selectedNode.data.config }));
    }
  }, [selectedNode]);

  if (!selectedNode) {
    return (
      <div className="h-full flex flex-col bg-white border-l border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">Properties</h2>
        </div>
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <div className="text-4xl mb-4">📋</div>
            <p className="text-gray-500 text-sm">Select a node to view its properties</p>
          </div>
        </div>
      </div>
    );
  }

  const { data } = selectedNode;
  const nodeStatus = workflowStatus?.nodes?.[selectedNode.id] || data;

  const getStatusBadge = (status: string) => {
    const styles = {
      running: 'bg-primary-100 text-primary-800 border-primary-200',
      completed: 'bg-success-100 text-success-800 border-success-200',
      failed: 'bg-danger-100 text-danger-800 border-danger-200',
      pending: 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return styles[status as keyof typeof styles] || styles.pending;
  };

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'neural': return '🧠';
      case 'symbolic': return '⚡';
      case 'meta': return '👁️';
      default: return '🤖';
    }
  };

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Properties</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-6">
          {/* Agent Header */}
          <div className="text-center pb-4 border-b border-gray-100">
            <div className="text-3xl mb-2">{getAgentIcon(data.type)}</div>
            <h3 className="font-semibold text-gray-800">{data.name}</h3>
            <p className="text-sm text-gray-500 font-mono">{data.agentId}</p>
          </div>

          {/* Status Overview */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-sm text-gray-700 mb-3">Status Overview</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Current Status</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusBadge(nodeStatus.status || data.status)}`}>
                  {(nodeStatus.status || data.status).charAt(0).toUpperCase() + (nodeStatus.status || data.status).slice(1)}
                </span>
              </div>

              {nodeStatus.executionTime && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Execution Time</span>
                  <span className="text-sm font-mono text-gray-800">{nodeStatus.executionTime}</span>
                </div>
              )}

              {nodeStatus.confidence !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Confidence</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${nodeStatus.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-mono text-gray-800">{Math.round(nodeStatus.confidence * 100)}%</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Configuration */}
          <div>
            <h4 className="font-medium text-sm text-gray-700 mb-3">Configuration</h4>
            <div className="space-y-3">
              {data.type === 'neural' && (
                <>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Max Length</label>
                    <input
                      type="number"
                      value={config.maxLength}
                      onChange={(e) => setConfig(prev => ({ ...prev, maxLength: parseInt(e.target.value) }))}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Model</label>
                    <select
                      value={config.model}
                      onChange={(e) => setConfig(prev => ({ ...prev, model: e.target.value }))}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      <option value="gpt-4">GPT-4</option>
                      <option value="claude-3-haiku">Claude 3 Haiku</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Temperature</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={config.temperature}
                      onChange={(e) => setConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>0</span>
                      <span className="font-mono">{config.temperature}</span>
                      <span>1</span>
                    </div>
                  </div>
                </>
              )}

              {data.type === 'symbolic' && (
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Validation Rules</label>
                  <div className="space-y-2">
                    {['schema_check', 'consistency_check', 'format_check'].map(rule => (
                      <label key={rule} className="flex items-center">
                        <input type="checkbox" defaultChecked className="mr-2" />
                        <span className="text-sm text-gray-700">{rule.replace('_', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {data.type === 'meta' && (
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Supervision Level</label>
                  <select className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                    <option value="basic">Basic Monitoring</option>
                    <option value="standard">Standard Supervision</option>
                    <option value="strict">Strict Validation</option>
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* Artifacts */}
          <div>
            <h4 className="font-medium text-sm text-gray-700 mb-3">Artifacts</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">Input Artifacts</span>
                <span className="text-sm font-mono text-gray-800">{nodeStatus.inputArtifacts || 0}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">Output Artifacts</span>
                <span className="text-sm font-mono text-gray-800">{nodeStatus.outputArtifacts || 0}</span>
              </div>
            </div>
          </div>

          {/* Agent Details */}
          <div>
            <h4 className="font-medium text-sm text-gray-700 mb-3">Agent Details</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Type:</span>
                <span className="capitalize text-gray-800">{data.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Version:</span>
                <span className="font-mono text-gray-800">v1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated:</span>
                <span className="font-mono text-gray-800">2025-01-01</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertiesPanel;