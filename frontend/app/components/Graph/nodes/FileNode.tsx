"use client";

import { FileCode } from "lucide-react";
import { Handle, Position } from "reactflow";

export default function FileNode({ data }: any) {

    return (

        <div className="bg-blue-950 border border-blue-500 rounded-lg px-4 py-2 min-w-[180px] shadow-lg">

            <Handle
                type="target"
                position={Position.Top}
            />

            <div className="flex items-center gap-2">

                <FileCode size={18} />

                <span className="font-medium">
                    {data.label}
                </span>

            </div>

            <Handle
                type="source"
                position={Position.Bottom}
            />

        </div>

    );

}