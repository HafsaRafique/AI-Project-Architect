"use client";

import {
  ReactFlow,
  Background,
  Controls,
} from "reactflow";

import "reactflow/dist/style.css";
import FileNode from "./Graph/nodes/FileNode";
import FunctionNode from "./Graph/nodes/FunctionNode";
import ClassNode from "./Graph/nodes/ClassNode";
import ModuleNode from "./Graph/nodes/ModuleNode";

// Define once, outside the component
const nodeTypes = {

    file: FileNode,

    function: FunctionNode,

    class: ClassNode,

    module: ModuleNode

};

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
        
         onNodeClick={(_, node) => {console.log(node); onNodeClick(node)}}
         
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}