import React from 'react';
import WorkflowCanvas from './components/WorkflowCanvas.tsx';

function App() {
  return (
    <div className="App">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">AI Orchestrator Platform - Phase 0</h1>
        <p className="text-sm">Agent orchestration with A2A protocol</p>
      </header>
      <main className="flex h-screen">
        <WorkflowCanvas />
      </main>
    </div>
  );
}

export default App;