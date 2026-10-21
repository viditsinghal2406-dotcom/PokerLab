import { useEffect, useState } from "react";

import { getDashboard, type DashboardResponse } from "../services/api";

export function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard().then(setData).catch((reason: Error) => setError(reason.message));
  }, []);

  return (
    <section className="page-stack analytics-page" aria-labelledby="dashboard-title">
      <div className="page-heading"><div><p className="eyebrow">Research workspace</p><h2 id="dashboard-title">Dashboard</h2><p className="page-subtitle">A concise view of your reproducible poker and forecasting work.</p></div><span className="status-pill">Virtual chips only</span></div>
      {error && <p className="error">{error}</p>}
      {!data && !error && <p className="m">Loading dashboard data…</p>}
      {data && (
        <>
          <div className="stat-grid dashboard-stats">
            <div className="ui-stat"><span>Experiments</span><strong>{data.experiments_count}</strong><span className="sr-only">Experiments: {data.experiments_count}</span><small>saved records</small></div>
            <div className="ui-stat"><span>Completed simulations</span><strong>{data.completed_jobs_count}</strong><small>backend jobs</small></div>
            <div className="ui-stat"><span>Strategy presets</span><strong>{data.strategy_configs_count}</strong><small>reusable configs</small></div>
            <div className="ui-stat"><span>Best recent condition</span><strong>{data.best_recent_condition ?? "n/a"}</strong><small>{data.best_recent_mean_bb_per_hand == null ? "No result yet" : `${data.best_recent_mean_bb_per_hand.toFixed(3)} BB/hand`}</small></div>
          </div>
          {!Array.isArray(data.recent_experiments) || data.recent_experiments.length === 0 ? (
            <p className="m">No experiments yet. Run one in Experiment Lab to populate this dashboard.</p>
          ) : (
            <ul>{data.recent_experiments.map((experiment) => (
              <li key={experiment.id}>{experiment.name} <span className="m">({new Date(experiment.created_at).toLocaleString()})</span></li>
            ))}</ul>
          )}
        </>
      )}
    </section>
  );
}
