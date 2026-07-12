import { Node, Edge } from "reactflow";

export function convertGraph(graph: any) {

    const nodes: Node[] = graph.nodes.map(
    (node: any, index: number) => ({

        id: node.id,

       data: {
    label: node.name ?? node.id,
    type: node.type,
    path: node.path
},

        position: {
            x: (index % 5) * 250,
            y: Math.floor(index / 5) * 120
        },

        type: "default"
    })
);
    

    const edges: Edge[] = graph.edges.map(
        (edge: any, index: number) => ({

            id: `${edge.source}-${edge.target}-${index}`,

            source: edge.source,

            target: edge.target,

            label: edge.relation,

            animated: edge.relation === "imports"
        })
    );

    return {
        nodes,
        edges
    };

}