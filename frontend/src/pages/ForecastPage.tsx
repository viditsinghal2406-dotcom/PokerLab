import { useState } from "react";

import { TimeSeriesChart } from "../components/charts/TimeSeriesChart";
import { runForecast, type ForecastResponse } from "../services/api";

const defaultSeries = Array.from({ length: 40 }, (_, index) =>
  20 + index * 0.2 + Math.sin(index / 3),
);

export function ForecastPage() {
  const [values, setValues] = useState(defaultSeries.join(", "));
  const [trainFraction, setTrainFraction] = useState(0.8);
  const [rollingOrigin, setRollingOrigin] = useState(false);
  const [result, setResult] = useState<ForecastResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    const series = values.split(",").map(Number);
    if (series.length < 12 || series.some((value) => !Number.isFinite(value))) {
      setError("Enter at least 12 comma-separated numeric values.");
      return;
    }
    try {
      setError(null);
      setResult(await runForecast(series, trainFraction, rollingOrigin));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Forecast analysis failed");
    }
  };

  return (
    <section className="panel analytics-page" aria-labelledby="forecast-title">
      <div className="page-heading"><div><p className="eyebrow">Model evaluation</p><h2 id="forecast-title">Forecasting Arena</h2><p className="page-subtitle">Chronological hold-out evaluation with no leakage.</p></div></div>
      <label className="series-input">Series
        <textarea value={values} onChange={(event) => setValues(event.target.value)} rows={3} />
      </label>
      <div className="controls">
        <label>Train fraction
          <input type="number" min="0.5" max="0.95" step="0.05" value={trainFraction} onChange={(event) => setTrainFraction(Number(event.target.value))} />
        </label>
        <label>Rolling origin
          <input type="checkbox" checked={rollingOrigin} onChange={(event) => setRollingOrigin(event.target.checked)} />
        </label>
      </div>
      <button type="button" onClick={run}>Run Forecast Arena</button>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="forecast-results">
          <p className="m">Train {result.train_size} / test {result.test_size}; chronological split; all tuning uses training data only.</p>
          <table>
            <thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>Bias</th><th>Residual ρ1</th></tr></thead>
            <tbody>{result.results.map((item) => <tr key={item.name}>
              <td>{item.name}</td><td>{item.metrics.mae.toFixed(3)}</td><td>{item.metrics.rmse.toFixed(3)}</td>
              <td>{item.metrics.mape == null ? "n/a" : `${item.metrics.mape.toFixed(1)}%`}</td>
              <td>{item.metrics.bias.toFixed(3)}</td><td>{item.metrics.residual_acf1.toFixed(2)}</td>
            </tr>)}</tbody>
          </table>
          <p className="m">MAPE is shown only when every held-out actual is positive. It is undefined or unstable around zero; compare MAE/RMSE as well.</p>
          <TimeSeriesChart title="Actual vs held-out forecasts" series={[
            {
              label: "Actual",
              values: Array(result.train_size).fill(Number.NaN).concat(result.actual),
              color: "#f4f7f5",
            },
            ...result.results.slice(0, 6).map((item, index) => ({
              label: item.name,
              values: Array(result.train_size).fill(Number.NaN).concat(item.forecast),
              color: ["#2f8f63", "#d23a32", "#e0b341", "#6aa6e8", "#b58be8", "#8fa096"][index],
            })),
          ]} />
        </div>
      )}
    </section>
  );
}
