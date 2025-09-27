import React from 'react';
import { Handle, Position } from 'reactflow';

interface AgentNodeProps {
  data: {
    agentId: string;
    name: string;
    type: string;
    status: string;
    executionTime?: string;
    confidence?: number;
  };
}

const AgentNode: React.FC<AgentNodeProps> = ({ data }) => {
  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'neural': return '🧠';
      case 'symbolic': return '⚡';
      case 'meta': return '👁️';
      default: return '🤖';
    }
  };

  const getNodeStyle = (type: string) => {
    switch (type) {
      case 'neural':
        return 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-300 shadow-blue-200/50';
      case 'symbolic':
        return 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-300 shadow-purple-200/50';
      case 'meta':
        return 'bg-gradient-to-br from-slate-50 to-slate-100 border-slate-300 shadow-slate-200/50';
      default:
        return 'bg-gradient-to-br from-slate-50 to-slate-100 border-slate-300 shadow-slate-200/50';
    }
  };

  const getStatusIndicator = (status: string) => {
    switch (status) {
      case 'running':
        return (
          <div className="relative">
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
            <div className="absolute inset-0 w-4 h-4 bg-blue-400 rounded-full animate-ping opacity-75"></div>
          </div>
        );
      case 'completed':
        return (
          <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'failed':
        return (
          <div className="w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      default:
        return <div className="w-4 h-4 bg-slate-400 rounded-full"></div>;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return 'Running';
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      default: return 'Pending';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div className={`relative px-5 py-4 shadow-xl rounded-xl border-2 ${getNodeStyle(data.type)} min-w-[260px] transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] cursor-pointer`}>
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-5 h-5 bg-blue-500 border-3 border-white rounded-full -top-2.5 shadow-lg"
      />

      {/* Header with Icon and Status */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            data.type === 'neural' ? 'bg-blue-200' :
            data.type === 'symbolic' ? 'bg-purple-200' :
            'bg-slate-200'
          }`}>
            <span className="text-xl">{getAgentIcon(data.type)}</span>
          </div>
          <div>
            <div className="font-bold text-sm text-slate-800 leading-tight">{data.name}</div>
            <div className="text-xs text-slate-500 font-mono uppercase tracking-wide">{data.agentId.split('_')[0]}</div>
          </div>
        </div>
        <div className="flex-shrink-0">
          {getStatusIndicator(data.status)}
        </div>
      </div>

      {/* Status Badge */}
      <div className="mb-3">
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(data.status)}`}>
          {getStatusText(data.status)}
        </span>
      </div>

      {/* Metrics */}
      {(data.executionTime || data.confidence !== undefined) && (
        <div className="space-y-2 mb-3">
          {data.executionTime && (
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-600 font-medium">Execution Time:</span>
              <span className="text-xs font-mono text-slate-800 bg-slate-200 px-2 py-1 rounded">{data.executionTime}</span>
            </div>
          )}

          {data.confidence !== undefined && (
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600 font-medium">Confidence:</span>
                <span className="text-xs font-mono text-slate-800">{Math.round(data.confidence * 100)}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-1.5">
                <div
                  className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${data.confidence * 100}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Agent Type Badge */}
      <div className="flex items-center justify-center">
        <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${
          data.type === 'neural' ? 'bg-blue-200 text-blue-800' :
          data.type === 'symbolic' ? 'bg-purple-200 text-purple-800' :
          'bg-slate-200 text-slate-800'
        }`}>
          {data.type.charAt(0).toUpperCase() + data.type.slice(1)} Agent
        </span>
      </div>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-5 h-5 bg-green-500 border-3 border-white rounded-full -bottom-2.5 shadow-lg"
      />
    </div>
  );
};

export default AgentNode;