"use client";

import { Package } from "lucide-react";
import { Handle, Position } from "reactflow";

export default function ModuleNode({ data }: any) {

    return (

        <div className="bg-orange-950 border border-orange-500 rounded-lg px-3 py-2">

            <Handle
                type="target"
                position={Position.Top}
            />

            <div className="flex items-center gap-2">

                <Package size={16} />

                {data.label}

            </div>

            <Handle
                type="source"
                position={Position.Bottom}
            />

        </div>

    );

}