import { lazy, Suspense, useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { LayoutDashboard, FlaskConical, LineChart, Play, Spade, UserRound, Beaker } from "lucide-react";

import { getHealth, type HealthResponse } from "../services/api";

const DashboardPage = lazy(() => import("../pages/DashboardPage").then((module) => ({ default: module.DashboardPage })));
const PokerArenaPage = lazy(() => import("../pages/PokerArenaPage").then((module) => ({ default: module.PokerArenaPage })));
const AtsaPage = lazy(() => import("../pages/AtsaPage").then((module) => ({ default: module.AtsaPage })));
const ForecastPage = lazy(() => import("../pages/ForecastPage").then((module) => ({ default: module.ForecastPage })));
const ExperimentsPage = lazy(() => import("../pages/ExperimentsPage").then((module) => ({ default: module.ExperimentsPage })));
const ProfilePage = lazy(() => import("../pages/ProfilePage").then((module) => ({ default: module.ProfilePage })));
const SimulationLabPage = lazy(() => import("../pages/SimulationLabPage").then((module) => ({ default: module.SimulationLabPage })));

const navigation = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/arena", label: "Poker Arena", icon: Spade },
  { to: "/lab", label: "Simulation Lab", icon: FlaskConical },
  { to: "/atsa", label: "ATSA Studio", icon: LineChart },
  { to: "/forecast", label: "Forecasting", icon: Play },
  { to: "/experiments", label: "Experiments", icon: Beaker },
  { to: "/profile", label: "Profile", icon: UserRound },
];

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getHealth().then(setHealth).catch((reason: Error) => setError(reason.message)); }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">P</span><div><h1>PokerLab</h1><small>Research workspace</small></div></div>
        <nav aria-label="Primary navigation">
          <span className="nav-section-label">Workspace</span>
          {navigation.slice(0, 2).map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}><Icon size={18} aria-hidden="true" /><span>{label}</span></NavLink>)}
          <span className="nav-section-label">Research</span>
          {navigation.slice(2).map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}><Icon size={18} aria-hidden="true" /><span>{label}</span></NavLink>)}
        </nav>
        <div className="sidebar-status" data-testid="api-status"><span className={health ? "status-dot online" : "status-dot"} />{health ? "API connected" : error ? "API unavailable" : "Connecting…"}</div>
      </aside>
      <main className="workspace">
        <header className="mobile-topbar"><div className="brand"><span className="brand-mark">P</span><h1>PokerLab</h1></div><span className={health ? "status-dot online" : "status-dot"} /></header>
        <Suspense fallback={<div className="route-loading">Loading workspace…</div>}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/arena" element={<PokerArenaPage />} />
            <Route path="/lab" element={<SimulationLabPage />} />
            <Route path="/atsa" element={<AtsaPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/experiments" element={<ExperimentsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  );
}

export default App;
