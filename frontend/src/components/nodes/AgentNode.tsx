import React from 'react';
import { Handle, Position } from 'reactflow';

interface AgentNodeProps {
  data: {
    agentId: string;
    name: string;
    type: string;
    status: string;
  };
}

const AgentNode: React.FC<AgentNodeProps> = ({ data }) => {
  const getNodeColor = (type: string) => {
    switch (type) {
      case 'neural': return 'bg-blue-100 border-blue-500';
      case 'symbolic': return 'bg-purple-100 border-purple-500';
      case 'meta': return 'bg-gray-100 border-gray-500';
      default: return 'bg-gray-100 border-gray-500';
    }
  };

  const getStatusIndicator = (status: string) => {
    switch (status) {
      case 'running': return '●';
      case 'completed': return '●';
      case 'failed': return '●';
      default: return '○';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-500';
      case 'completed': return 'text-green-500';
      case 'failed': return 'text-red-500';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className={`px-4 py-2 shadow-md rounded-md border-2 ${getNodeColor(data.type)} min-w-[200px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-blue-500" />

      <div className="flex items-center justify-between">
        <div className="text-lg font-bold">{data.name}</div>
        <div className={`text-sm font-bold ${getStatusColor(data.status)}`}>
          {getStatusIndicator(data.status)}
        </div>
      </div>

      <div className="text-xs text-gray-600 mt-1">
        {data.agentId}
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-green-500" />
    </div>
  );
};

export default AgentNode;