"use client";

import { useState } from "react";

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
  const [activeTab, setActiveTab] = useState<"graph" | "code">("graph");
  console.log("Workspace rendered");
  console.log("Active tab:", activeTab);
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
            <div className="h-full flex flex-col">

              
              <div className="flex border-b border-slate-800">

                <button
                  onClick={() => setActiveTab("graph")}
                  className={`px-4 py-2 transition-colors ${
                    activeTab === "graph"
                      ? "bg-slate-800 text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Architecture
                </button>

                <button
                  onClick={() => setActiveTab("code")}
                  className={`px-4 py-2 transition-colors ${
                    activeTab === "code"
                      ? "bg-slate-800 text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Code
                </button>

              </div>

             
              <div className="flex-1 overflow-hidden">

                {activeTab === "graph" ? (
                  <GraphPanel
                    onOpenFile={() => setActiveTab("code")}
                  />
                ) : (
                  <CodeViewer />
                )}

              </div>

            </div>
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