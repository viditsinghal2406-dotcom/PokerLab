import { useState } from "react";

import { runAtsa, type AtsaResponse } from "../services/api";
import { BarSeriesChart } from "../components/charts/BarSeriesChart";
import { TimeSeriesChart } from "../components/charts/TimeSeriesChart";

const defaultSeries = Array.from({ length: 40 }, (_, index) =>
  100 + index * 0.25 + Math.sin(index / 3) * 2,
);

export function AtsaPage() {
  const [values, setValues] = useState(defaultSeries.join(", "));
  const [order, setOrder] = useState<[number, number, number]>([1, 0, 1]);
  const [horizon, setHorizon] = useState(6);
  const [lags, setLags] = useState(8);
  const [result, setResult] = useState<AtsaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    const series = values.split(",").map(Number);
    if (series.some((value) => !Number.isFinite(value)) || series.length < 8) {
      setError("Enter at least 8 comma-separated numeric values.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setResult(await runAtsa(series, order, horizon, lags));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "ATSA analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel analytics-page" aria-labelledby="atsa-title">
      <div className="page-heading"><div><p className="eyebrow">Statistical workspace</p><h2 id="atsa-title">ATSA diagnostics</h2><p className="page-subtitle">Stationarity, autocorrelation and ARIMA diagnostics with reproducible inputs.</p></div></div>
      <label className="series-input">Series
        <textarea value={values} onChange={(event) => setValues(event.target.value)} rows={3} />
      </label>
      <div className="controls">
        <label>AR <input type="number" min="0" max="5" value={order[0]} onChange={(event) => setOrder([Number(event.target.value), order[1], order[2]])} /></label>
        <label>Diff <input type="number" min="0" max="5" value={order[1]} onChange={(event) => setOrder([order[0], Number(event.target.value), order[2]])} /></label>
        <label>MA <input type="number" min="0" max="5" value={order[2]} onChange={(event) => setOrder([order[0], order[1], Number(event.target.value)])} /></label>
        <label>Horizon <input type="number" min="1" max="1000" value={horizon} onChange={(event) => setHorizon(Number(event.target.value))} /></label>
        <label>Lags <input type="number" min="1" max="100" value={lags} onChange={(event) => setLags(Number(event.target.value))} /></label>
      </div>
      <button type="button" onClick={analyze} disabled={loading}>{loading ? "Analyzing…" : "Run ATSA"}</button>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="atsa-results">
          <div className="metrics">
            <p>ADF: {result.adf.statistic.toFixed(3)} (p={result.adf.p_value.toFixed(3)}) · {result.adf.conclusion}</p>
            <p>KPSS: {result.kpss.statistic.toFixed(3)} (p={result.kpss.p_value.toFixed(3)}) · {result.kpss.conclusion}</p>
            <p>ARIMA({result.arima_order.join(",")}) · AIC {result.aic.toFixed(2)} · BIC {result.bic.toFixed(2)} · Ljung-Box p {result.ljung_box_p_value.toFixed(3)}</p>
          </div>
          <TimeSeriesChart title="Forecast with intervals" series={[
            { label: "Forecast", values: result.forecast, color: "#2f8f63" },
            { label: "Lower", values: result.lower, color: "#d23a32" },
            { label: "Upper", values: result.upper, color: "#e0b341" },
          ]} />
          <div className="chart-grid">
            <BarSeriesChart title="ACF" values={result.acf} />
            <BarSeriesChart title="PACF" values={result.pacf} />
          </div>
          <TimeSeriesChart title="ARIMA residuals" series={[{ label: "Residual", values: result.residuals, color: "#b58be8" }]} />
        </div>
      )}
    </section>
  );
}
