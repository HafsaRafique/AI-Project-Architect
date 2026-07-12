"use client";

import {
  ReactFlow,
  Background,
  Controls,
} from "reactflow";

import "reactflow/dist/style.css";

// Define once, outside the component
const nodeTypes = Object.freeze({});
const edgeTypes = Object.freeze({});

type Props = {
  nodes: any[];
  edges: any[];
};

export default function ArchitectureGraph({
  nodes,
  edges,
}: Props) {
  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}