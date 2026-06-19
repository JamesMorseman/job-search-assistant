import { NavLink } from "react-router-dom";

import AtlasMark from "./AtlasMark";
import {
  AskAtlasIcon,
  CommandCenterIcon,
  OpportunityDetailIcon,
  PipelineIcon,
  RadarIcon,
} from "./NavIcons";

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
      { label: "Ask Atlas", path: "/ask-atlas", Icon: AskAtlasIcon },
    ],
  },
];

export default function Sidebar() {
  return (
    <aside className="atlas-sidebar" aria-label="ATLAS navigation">
      <div className="atlas-brand">
        <span className="atlas-mark" aria-hidden="true">
          <AtlasMark className="atlas-mark-svg" />
        </span>
        <div>
          <p className="atlas-brand-wordmark">ATLAS</p>
          <p className="atlas-brand-kicker">Career Mission Control</p>
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

      <p className="atlas-mission-strip">
        ATLAS scans. Atlas interprets. Ask Atlas communicates. Pipeline executes.
      </p>

      <div className="atlas-sidebar-footer">
        <span>ATLAS Local</span>
        <strong>Runtime Demo Ready</strong>
      </div>
    </aside>
  );
}
