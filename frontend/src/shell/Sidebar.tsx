import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Command Center", path: "/command-center" },
  { label: "Radar", path: "/radar" },
  { label: "Pipeline", path: "/pipeline" },
  { label: "Opportunity Detail", path: "/opportunity-detail" },
  { label: "Ask Atlas", path: "/ask-atlas" }
];

export default function Sidebar() {
  return (
    <aside className="atlas-sidebar" aria-label="ATLAS navigation">
      <div className="atlas-brand">
        <span className="atlas-mark" aria-hidden="true">
          A
        </span>
        <div>
          <p className="atlas-brand-kicker">ATLAS</p>
          <h1>Career Mission Control</h1>
        </div>
      </div>

      <nav className="atlas-nav">
        {navItems.map((item) => (
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

      <div className="atlas-sidebar-footer">
        <span>Desktop Shell</span>
        <strong>Package 1</strong>
      </div>
    </aside>
  );
}
