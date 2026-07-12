"use client";

import { FunctionSquare } from "lucide-react";
import { Handle, Position } from "reactflow";

export default function FunctionNode({ data }: any) {

    return (

        <div className="bg-green-950 border border-green-500 rounded-lg px-3 py-2">

            <Handle
                type="target"
                position={Position.Top}
            />

            <div className="flex items-center gap-2">

                <FunctionSquare size={16} />

                {data.label}

            </div>

            <Handle
                type="source"
                position={Position.Bottom}
            />

        </div>

    );

}