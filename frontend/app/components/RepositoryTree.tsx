"use client";

import { useRepository } from "../context/RepositoryContext";
import TreeNode from "./TreeNode";

export default function RepositoryTree() {
  const { repository } = useRepository();

  if (!repository)
    return (
      <p className="text-slate-400 text-sm">
        Upload a repository...
      </p>
    );

  return (
    <div className="space-y-1">
      {repository.tree.map((node: any, index: number) => (
        <TreeNode
          key={index}
          node={node}
        />
      ))}
    </div>
  );
}