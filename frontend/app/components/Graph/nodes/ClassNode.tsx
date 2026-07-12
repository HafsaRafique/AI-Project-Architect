"use client";

import { Boxes } from "lucide-react";
import { Handle, Position } from "reactflow";

export default function ClassNode({ data }: any) {

    return (

        <div className="bg-purple-950 border border-purple-500 rounded-lg px-3 py-2">

            <Handle
                type="target"
                position={Position.Top}
            />

            <div className="flex items-center gap-2">

                <Boxes size={16} />

                {data.label}

            </div>

            <Handle
                type="source"
                position={Position.Bottom}
            />

        </div>

    );

}