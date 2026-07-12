"use client";

import { useRepository } from "../context/RepositoryContext";
import ArchitectureGraph from "./ArchitectureGraph";
import { convertGraph } from "../../lib/convertGraph";
import { useMemo } from "react";

type Props = {
    onOpenFile: () => void;
};

export default function GraphPanel({
    onOpenFile
}: Props) {
   const {
    repository,
    setSelectedFile,
} = useRepository();
    
    const { nodes, edges } = useMemo(() => {

        if (!repository?.graph) {
            return {
                nodes: [],
                edges: []
            };
        }

        return convertGraph(repository.graph);

    }, [repository]);

    return (
        <ArchitectureGraph
    nodes={nodes}
    edges={edges}
    onNodeClick={(node) => {
        setSelectedFile(node.data.path);
        onOpenFile();

    }}
/>
    );
}