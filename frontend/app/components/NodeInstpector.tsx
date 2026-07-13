"use client";

import Markdown from "react-markdown";

type Props = {
    analysis: string;
    node: any;
};

export default function NodeInspector({
    analysis,
    node
}: Props) {

    if (!node) {
        return (
            <div className="p-4 text-slate-400">
                Click a graph node
            </div>
        );
    }


    return (
        <div className="
            w-96
            border-l
            border-slate-800
            p-4
            overflow-y-auto
        ">

            <h2 className="text-xl font-bold mb-4">
                {node.data.label}
            </h2>


            <Markdown>
                {analysis}
            </Markdown>

        </div>
    );
}