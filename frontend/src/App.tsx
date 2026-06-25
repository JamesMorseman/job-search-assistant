import { Navigate, Route, Routes } from "react-router-dom";

import AppShell from "./shell/AppShell";
import AskAtlas from "./workspaces/AskAtlas";
import BaseResumeLibrary from "./workspaces/BaseResumeLibrary";
import CommandCenter from "./workspaces/CommandCenter";
import FirmRepository from "./workspaces/FirmRepository";
import OpportunityDetail from "./workspaces/OpportunityDetail";
import OpportunityDetailSurface from "./workspaces/OpportunityDetailSurface";
import Pipeline from "./workspaces/Pipeline";
import Radar from "./workspaces/Radar";
import SettingsAbout from "./workspaces/SettingsAbout";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/command-center" replace />} />
        <Route path="command-center" element={<CommandCenter />} />
        <Route path="radar" element={<Radar />} />
        <Route path="pipeline" element={<Pipeline />} />
        <Route path="opportunity-detail" element={<OpportunityDetail />} />
        <Route path="opportunities/:jobId" element={<OpportunityDetailSurface />} />
        <Route path="base-resumes" element={<BaseResumeLibrary />} />
        <Route path="firms" element={<FirmRepository />} />
        <Route path="ask-atlas" element={<AskAtlas />} />
        <Route path="settings" element={<SettingsAbout />} />
        <Route path="*" element={<Navigate to="/command-center" replace />} />
      </Route>
    </Routes>
  );
}
