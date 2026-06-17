import { Outlet } from "react-router-dom";

import ContextPanel from "./ContextPanel";
import Sidebar from "./Sidebar";
import "./shell.css";

export default function AppShell() {
  return (
    <div className="atlas-shell min-h-screen">
      <Sidebar />
      <main className="atlas-workspace" aria-label="ATLAS workspace">
        <Outlet />
      </main>
      <ContextPanel />
    </div>
  );
}
