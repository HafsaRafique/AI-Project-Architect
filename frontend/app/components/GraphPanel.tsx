"use client";

import { useRepository } from "../context/RepositoryContext";
import ArchitectureGraph from "./ArchitectureGraph";
import { convertGraph } from "../../lib/convertGraph";
import { useMemo } from "react";

export default function GraphPanel() {
    const { repository } = useRepository();

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
        />
    );
}