import { useState } from "react";

import { runExperiment, type ExperimentResponse } from "../services/api";

export function ExperimentsPage() {
  const [kind, setKind] = useState("E");
  const [trials, setTrials] = useState(3);
  const [hands, setHands] = useState(60);
  const [result, setResult] = useState<ExperimentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    try {
      setError(null);
      setResult(await runExperiment("PokerLab experiment", "", kind, trials, hands));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Experiment failed");
    }
  };

  return (
    <section className="panel analytics-page" aria-labelledby="experiments-title">
      <div className="page-heading"><div><p className="eyebrow">Comparative research</p><h2 id="experiments-title">Experiment Lab</h2><p className="page-subtitle">Compare policies and variants using common seeds and confidence intervals.</p></div></div>
      <div className="controls">
        <label>Experiment
          <select value={kind} onChange={(event) => setKind(event.target.value)}>
            <option value="A">A: Vidit vs baseline policies</option>
            <option value="B">B: Vidit parameter sensitivity</option>
            <option value="C">C: Policy comparison</option>
            <option value="D">D: Variant comparison</option>
            <option value="E">E: Vidit vs other policies</option>
            <option value="F">F: Vidit across variants</option>
          </select>
        </label>
        <label>Trials
          <input type="number" min="1" max="20" value={trials} onChange={(event) => setTrials(Number(event.target.value))} />
        </label>
        <label>Hands/trial
          <input type="number" min="2" max="500" value={hands} onChange={(event) => setHands(Number(event.target.value))} />
        </label>
      </div>
      <button type="button" onClick={run}>Run experiment</button>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="experiment-results">
          <p className="m">Common seeds: {result.seeds.join(", ")} · {result.trials} trials × {result.hands} hands · metric: {result.metric}</p>
          <table>
            <thead><tr><th>Condition</th><th>Mean BB/hand ±95% CI</th><th>SD/hand</th><th>Avg max drawdown</th><th>Biggest win</th></tr></thead>
            <tbody>{result.results.map((item) => <tr key={item.label}>
              <td>{item.label}</td>
              <td>{item.mean_bb_per_hand.toFixed(3)} ± {item.ci95 == null ? "n/a" : item.ci95.toFixed(3)}</td>
              <td>{item.sd_bb_per_hand == null ? "n/a" : item.sd_bb_per_hand.toFixed(3)}</td>
              <td>{item.average_max_drawdown.toFixed(2)}</td>
              <td>{item.biggest_win.toFixed(2)}</td>
            </tr>)}</tbody>
          </table>
          <p className="m">These are realized observations from virtual-chip simulations, not causal claims. Download the saved record from the experiment API.</p>
        </div>
      )}
    </section>
  );
}
