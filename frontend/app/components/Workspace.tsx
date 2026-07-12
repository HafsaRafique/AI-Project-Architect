"use client";

import {
  Panel,
  Group,
  Separator,
} from "react-resizable-panels";

import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import CodeViewer from "./CodeViewer";
import AgentPanel from "./AgentPanel";
import GraphPanel from "./GraphPanel";

export default function Workspace() {
  return (
    <main className="h-screen flex flex-col bg-slate-950 text-white">

      <Navbar />

      <div className="flex-1 overflow-hidden">

        <Group
          orientation="horizontal"
          className="h-full"
        >
          <Panel
            defaultSize={20}
            minSize={15}
          >
            <Sidebar />
          </Panel>

          <Separator className="w-1 bg-slate-800 hover:bg-blue-500 cursor-col-resize transition-colors" />

          <Panel
            defaultSize={55}
            minSize={30}
          >
            <GraphPanel />
          </Panel>

          <Separator className="w-1 bg-slate-800 hover:bg-blue-500 cursor-col-resize transition-colors" />

          <Panel
            defaultSize={25}
            minSize={20}
          >
            <AgentPanel />
          </Panel>

        </Group>

      </div>

    </main>
  );
}