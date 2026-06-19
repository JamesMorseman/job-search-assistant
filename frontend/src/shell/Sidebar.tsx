import { NavLink } from "react-router-dom";

const navGroups = [
  {
    label: "Discover",
    items: [
      { label: "Command Center", path: "/command-center" },
      { label: "Radar", path: "/radar" },
    ],
  },
  {
    label: "Execute",
    items: [
      { label: "Pipeline", path: "/pipeline" },
      { label: "Opportunity Detail", path: "/opportunity-detail" },
      { label: "Ask Atlas", path: "/ask-atlas" },
    ],
  },
];

export default function Sidebar() {
  return (
    <aside className="atlas-sidebar" aria-label="ATLAS navigation">
      <div className="atlas-brand">
        <span className="atlas-mark" aria-hidden="true">
          <span className="atlas-mark-ring" />
          <span className="atlas-mark-dot" />
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
              <span className="atlas-nav-dot" aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      ))}

      <div className="atlas-sidebar-footer">
        <span>ATLAS Local</span>
        <strong>Runtime Demo Ready</strong>
      </div>
    </aside>
  );
}
