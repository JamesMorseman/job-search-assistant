import { NavLink } from "react-router-dom";

import AtlasMark from "./AtlasMark";
import {
  AskAtlasIcon,
  BaseResumesIcon,
  CommandCenterIcon,
  FirmsIcon,
  MissionExecuteIcon,
  MissionInterpretIcon,
  MissionScanIcon,
  OpportunityDetailIcon,
  PipelineIcon,
  RadarIcon,
  SettingsIcon,
} from "./NavIcons";

const missionSteps = [
  { label: "ATLAS scans.", Icon: MissionScanIcon },
  { label: "Atlas interprets.", Icon: MissionInterpretIcon },
  { label: "Ask Atlas communicates.", Icon: AskAtlasIcon },
  { label: "Pipeline executes.", Icon: MissionExecuteIcon },
];

const navGroups = [
  {
    label: "Discover",
    items: [
      { label: "Command Center", path: "/command-center", Icon: CommandCenterIcon },
      { label: "Radar", path: "/radar", Icon: RadarIcon },
    ],
  },
  {
    label: "Execute",
    items: [
      { label: "Pipeline", path: "/pipeline", Icon: PipelineIcon },
      { label: "Opportunity Detail", path: "/opportunity-detail", Icon: OpportunityDetailIcon },
      { label: "Base Resume Library", path: "/base-resumes", Icon: BaseResumesIcon },
      { label: "Firm Repository", path: "/firms", Icon: FirmsIcon },
      { label: "Ask Atlas", path: "/ask-atlas", Icon: AskAtlasIcon },
      { label: "Settings / About", path: "/settings", Icon: SettingsIcon },
    ],
  },
];

export default function Sidebar() {
  return (
    <aside className="atlas-sidebar" aria-label="ATLAS navigation">
      <div className="atlas-brand">
        <div className="atlas-mark" aria-hidden="true">
          <AtlasMark className="atlas-mark-svg" />
        </div>
        <div className="atlas-brand-lockup">
          <p className="atlas-brand-wordmark">
            ATLAS<span className="atlas-brand-wordmark-accent">.</span>
          </p>
          <p className="atlas-brand-kicker">Career Mission Control</p>
          <p className="atlas-brand-subline">Signal detection &amp; opportunity intelligence</p>
        </div>
      </div>

      {navGroups.map((group) => (
        <nav className="atlas-nav" aria-label={group.label} key={group.label}>
          <p className="atlas-nav-group-label">{group.label}</p>
          {group.items.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "atlas-nav-link is-active" : "atlas-nav-link"
              }
            >
              <span className="atlas-nav-icon" aria-hidden="true">
                <item.Icon className="atlas-nav-icon-svg" />
              </span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      ))}

      <ul className="atlas-mission-strip" role="list" aria-label="ATLAS mission sequence">
        {missionSteps.map((step) => (
          <li key={step.label} role="listitem">
            <span className="atlas-mission-strip-icon" aria-hidden="true">
              <step.Icon className="atlas-mission-strip-icon-svg" />
            </span>
            <span>{step.label}</span>
          </li>
        ))}
      </ul>

      <div className="atlas-sidebar-footer">
        <span className="atlas-sidebar-footer-dot" aria-hidden="true" />
        <span>ATLAS Local</span>
        <strong>Internal Demo Check</strong>
      </div>
    </aside>
  );
}
