"use client"
import { ChevronRight, ChevronDown, Folder, File } from "lucide-react";
import { useState } from "react";

import { useRepository } from "../context/RepositoryContext";


//recursive appraoch
type Node = {
    name : string;
    path: string
    type : "Folder" | "File";
    children?: Node[];



};
type Props = {
  node: Node;
};

export default function TreeNode({node}: Props){
    const [open, setOpen] = useState(true);
    const { selectedFile, setSelectedFile } = useRepository();

    if (node.type == "File"){
        return(
        <div className="flex items-center gap-2 py-1 pl-6 text-sm hover:bg-slate-800 rounded cursor-pointer">
            <File size={15} />
            {node.name}
         </div>
        );
    }
    return(
        <div>

            <div onClick= {()=> setOpen(!open) }  className="flex items-center gap-2 py-1 cursor-pointer hover:bg-slate-800 rounded"
      >
       {open ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
        <Folder size={15} />
        <span className="font-medium">{node.name}</span>         

            </div>
{open && (
        <div className="ml-4">
          {node.children?.map((child, index) => (
            <TreeNode
              key={index}
              node={child}
            />
          ))}
        </div>

        
      )}

      <div
    onClick={() => setSelectedFile(node.path)}
    className={`flex items-center gap-2 py-1 pl-6 text-sm rounded cursor-pointer
    ${
        selectedFile === node.name
            ? "bg-blue-600"
            : "hover:bg-slate-800"
    }`}
>
    <File size={15} />
    {node.name}
</div>
    </div>
    );
};