import React from 'react';
import { Node } from 'reactflow';

interface PropertiesPanelProps {
  selectedNode: Node | null;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ selectedNode }) => {
  if (!selectedNode) {
    return (
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Properties</h2>
        <p className="text-gray-500">Select a node to view its properties</p>
      </div>
    );
  }

  const { data } = selectedNode;

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Properties</h2>

      <div className="space-y-4">
        {/* Agent Info */}
        <div>
          <h3 className="font-medium text-sm text-gray-700 mb-2">Agent Information</h3>
          <div className="space-y-2">
            <div>
              <label className="block text-xs font-medium text-gray-500">Name</label>
              <div className="text-sm">{data.name}</div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">Agent ID</label>
              <div className="text-sm font-mono">{data.agentId}</div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">Type</label>
              <div className="text-sm capitalize">{data.type}</div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">Status</label>
              <div className="text-sm capitalize">{data.status}</div>
            </div>
          </div>
        </div>

        {/* Configuration */}
        <div>
          <h3 className="font-medium text-sm text-gray-700 mb-2">Configuration</h3>
          <div className="space-y-2">
            <div>
              <label className="block text-xs font-medium text-gray-500">Max Length</label>
              <input
                type="number"
                defaultValue={200}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">Model</label>
              <select className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option>gpt-3.5-turbo</option>
                <option>gpt-4</option>
              </select>
            </div>
          </div>
        </div>

        {/* Execution Status */}
        <div>
          <h3 className="font-medium text-sm text-gray-700 mb-2">Execution Status</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Status</span>
              <span className={`text-xs px-2 py-1 rounded ${
                data.status === 'running' ? 'bg-blue-100 text-blue-800' :
                data.status === 'completed' ? 'bg-green-100 text-green-800' :
                data.status === 'failed' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {data.status}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Execution Time</span>
              <span className="text-xs">--</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Confidence</span>
              <span className="text-xs">--</span>
            </div>
          </div>
        </div>

        {/* Artifacts */}
        <div>
          <h3 className="font-medium text-sm text-gray-700 mb-2">Artifacts</h3>
          <div className="space-y-1">
            <div className="text-xs text-gray-500">Input Artifacts: 0</div>
            <div className="text-xs text-gray-500">Output Artifacts: 0</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertiesPanel;