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

import { Node, Edge } from "reactflow";

type Props = {
  nodes: Node[];
  edges: Edge[];
  onNodeClick: (node: Node) => void;
};

export default function ArchitectureGraph({
  nodes,
  edges,
   onNodeClick,
}: Props) {
  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
       
        fitView
         onNodeClick={(_, node) => onNodeClick(node)}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}