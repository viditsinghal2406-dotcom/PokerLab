import { useState } from "react";

import { Button, Card, Stat } from "../components/ui";
import { apiBaseUrl } from "../services/api";

export function SimulationLabPage() {
  const [hands, setHands] = useState(100);
  const [players, setPlayers] = useState(3);
  const [status, setStatus] = useState("Ready");

  const start = async () => {
    setStatus("Starting…");
    const response = await fetch(`${apiBaseUrl}/jobs/simulations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed: Date.now() % 2 ** 32, variant: "holdem", player_count: players, hands }),
    });
    setStatus(response.ok ? "Queued" : "Unable to start");
  };

  return (
    <div className="page-stack analytics-page">
      <div className="page-heading"><div><p className="eyebrow">Monte Carlo workspace</p><h2>Simulation Lab</h2><p className="page-subtitle">Run reproducible virtual-chip experiments with backend-controlled state.</p></div><Button onClick={() => void start()}>Start simulation</Button></div>
      <Card className="lab-config research-card">
        <div className="controls">
          <label>Variant<select><option>Hold'em</option></select></label>
          <label>Players<select value={players} onChange={(event) => setPlayers(Number(event.target.value))}>{[2, 3, 4, 6, 9].map((value) => <option key={value}>{value}</option>)}</select></label>
          <label>Hands<select value={hands} onChange={(event) => setHands(Number(event.target.value))}>{[100, 1000, 10000, 100000].map((value) => <option key={value}>{value.toLocaleString()}</option>)}</select></label>
        </div>
        <div className="stat-grid"><Stat label="Status" value={status} /><Stat label="Seed" value="Generated on start" /><Stat label="Mode" value="Virtual chips" /></div>
      </Card>
    </div>
  );
}
