import { Outlet } from "react-router-dom";

import ContextPanel from "./ContextPanel";
import { ContextPanelProvider } from "./ContextPanelContext";
import Sidebar from "./Sidebar";
import "./shell.css";

export default function AppShell() {
  return (
    <ContextPanelProvider>
      <div className="atlas-shell min-h-screen">
        <Sidebar />
        <div className="atlas-workspace-column">
          <main className="atlas-workspace" aria-label="ATLAS workspace">
            <Outlet />
          </main>
          <footer className="atlas-mission-footer" aria-label="ATLAS mission summary">
            <p>ATLAS scans. Atlas interprets. Ask Atlas communicates. Pipeline executes.</p>
          </footer>
        </div>
        <ContextPanel />
      </div>
    </ContextPanelProvider>
  );
}
