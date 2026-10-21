# PokerLab

PokerLab is a dark-first educational poker simulation and time-series analysis
workspace. The backend is the source of truth for game state, legal actions,
simulations, and statistical results.

## Current status

The repository contains the working FastAPI backend, React/Vite frontend,
backend-authoritative poker table, simulation and analytics workflows,
persisted experiment/history APIs, reports, Docker configuration, and browser
tests. Use [RUN.md](RUN.md) for the complete Windows, local, test, and Docker
setup instructions.

## Local development

### Backend

```powershell
.\pokerlabs\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

The project virtual environment is named `pokerlabs` and lives at
`.\pokerlabs`. The root [requirements.txt](./requirements.txt) delegates to
the backend dependency manifest at
[backend/requirements.txt](./backend/requirements.txt).

The API is available at <http://localhost:8001>, with interactive docs at
<http://localhost:8001/docs>. The frontend's local Vite proxy targets port
8001.

### Persistence and jobs

The backend creates a local SQLite database from `DATABASE_URL` at startup.
Simulation jobs can be started with `POST /api/v1/jobs/simulations`, polled
with `GET /api/v1/jobs/simulations/{id}`, cancelled with
`POST /api/v1/jobs/simulations/{id}/cancel`, and read after completion with
`GET /api/v1/jobs/simulations/{id}/result`. Jobs are bounded to 10,000 hands
per request and retain their seed and per-hand results for reproducibility.

Experiment Lab runs the A-F policy and variant comparisons with common trial
seeds, virtual-chip outcomes, and 95% confidence intervals:

```powershell
curl -X POST http://localhost:8001/api/v1/experiments/run `
  -H "Content-Type: application/json" `
  -d '{"name":"Vidit comparison","kind":"E","trials":3,"hands":60}'
```

The returned experiment is persisted in SQLite. Retrieve it with
`GET /api/v1/experiments/{id}` or download its CSV record with
`GET /api/v1/experiments/{id}/export.csv`. Results are realized observations,
not causal claims; experiments use virtual chips only.

## Reports and dashboard

The dashboard reads its counts and recent experiment list from
`GET /api/v1/dashboard` and shows an empty state when no persisted data exists.
Each saved experiment supports:

- `GET /api/v1/experiments/{id}/report.html` for a standalone HTML report
- `GET /api/v1/experiments/{id}/report.pdf` for a printable PDF report
- `GET /api/v1/experiments/{id}/export.csv` for tabular CSV output
- `GET /api/v1/experiments/{id}/export.parquet` for analytics workflows

Parquet support is provided by `pyarrow` in the backend dependency manifest.

### Frontend

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1 --port 5174
```

The frontend is available at <http://localhost:5174>. See
[RUN.md](RUN.md) for the default Vite port and troubleshooting details.

## Testing

```powershell
& .\pokerlabs\Scripts\python.exe -m pytest backend

cd frontend
npm.cmd test -- --run
npm.cmd run build
npm.cmd run test:e2e -- --reporter=line
```

Install the Playwright browser once with
`npx.cmd playwright install chromium`. The browser suite requires the backend
and frontend to be running. See [RUN.md](RUN.md) for coverage commands.

## Architecture

```text
Browser (React/Vite/TypeScript/Recharts)
              |
              v
FastAPI /api/v1  ---- SQLAlchemy ---- SQLite volume
       |                         \
       +-- simulation engine      +-- HTML/PDF/CSV/Parquet exports
       +-- ATSA/forecasting
       +-- background jobs
```

The backend owns game state, legal actions, hidden-card boundaries, simulation
seeds, and statistical calculations. The frontend requests data and renders
it; it does not calculate poker outcomes or statistics.

## Feature list

- Seeded 2–9 player poker dealing, evaluation, side pots, and street-by-street
  table actions.
- Vidit Mode and comparison policies with configurable aggression, bluff, risk,
  and bounded Monte Carlo equity.
- Background simulation jobs with progress, cancellation, and reproducibility.
- ATSA diagnostics, true ARIMA, forecast intervals, and Forecasting Arena.
- Reproducible A-F experiments with confidence intervals.
- SQLite history for experiments, strategy presets, ATSA runs, and forecasts.
- HTML, PDF, CSV, and Parquet exports.
- Dark-first responsive React interface with lazy-loaded analytics modules,
  self-hosted fonts, CSS design tokens, and Lucide icons.

## Docker setup

Docker Compose uses ports `8001` (API) and `5174` (frontend) to avoid common
local development port collisions:

```powershell
docker compose up --build
curl http://localhost:8001/api/v1/health
```

SQLite data is stored in the `pokerlab-data` volume and export storage in
`pokerlab-exports`. Stop the stack with `docker compose down`.

## API overview

- `GET /api/v1/health`
- `POST /api/v1/simulations/multiway`
- `POST /api/v1/tables`, `GET /api/v1/tables/{id}`,
  `POST /api/v1/tables/{id}/actions`
- `POST /api/v1/jobs/simulations` and job status/result/cancel routes
- `POST /api/v1/analytics/atsa`
- `POST /api/v1/analytics/forecast`
- `GET /api/v1/analytics/series` and `/analytics/history`
- `POST /api/v1/experiments/run`
- Experiment HTML/PDF/CSV/Parquet export routes
- Dashboard and strategy-config management routes

## Statistical methods for a viva

**SMA** averages the most recent fixed-size window, reducing short-term noise
while responding more slowly when the window is large. **SES** maintains one
smoothed level and weights recent observations more heavily using alpha.

**Holt's method** extends exponential smoothing with a second state for trend,
using alpha for level updates and beta for trend updates. **ACF** measures the
correlation between a series and lagged copies of itself, which helps identify
repeated temporal structure. **PACF** measures the correlation at a lag after
removing the effects of shorter lags, helping select autoregressive terms.

**ADF** tests a null hypothesis of a unit root; a small p-value supports
rejecting non-stationarity under its assumptions. **KPSS** reverses the
perspective by testing stationarity as the null, so using both tests gives a
more balanced diagnosis. **Differencing** subtracts adjacent observations to
remove level trends before modeling.

**ARIMA(p,d,q)** combines autoregression, differencing, and moving-average
residual terms. Parameters are fit with statsmodels; AIC and BIC compare fit
with complexity penalties, while Ljung-Box tests whether residual
autocorrelation remains. Forecast intervals represent model uncertainty, not
guaranteed bounds.

**Linear trend regression** estimates an ordinary least-squares line against
time. Forecasting Arena uses a chronological holdout, trains models only on
the training segment, and reports MAE, RMSE, conditional MAPE, bias, and
residual lag-1 autocorrelation. Rolling-origin evaluation repeats this process
at successive time points.

## Capturing screenshots

Start the backend and frontend, open `http://localhost:5174` for the documented
local workflow or Docker, then use the browser's developer-tools screenshot
command. Automated poker screenshots are produced by the Playwright suite
under `frontend/test-results`. Capture the dashboard, playable table, ATSA
diagnostics, Forecasting Arena, and Experiment Lab separately so each state
contains real backend data.

## Known limitations

- Multiway betting now has shared street state, legal bounds, all-ins, and
  showdown handling, but the simulation-job experiment runner still samples
  deterministic hands rather than modeling every opponent action.
- Saved analytics history has API support; a complete history-management UI for
  every persisted entity is still smaller than the intended product surface.
- Simulation Lab does not yet expose 100,000-hand requests because the backend
  safety limit remains 10,000.
- Optional stopping rules, multiple independent trial controls, and bankroll
  moving-average charts are not complete.
- The current Simulation Lab UI is a configuration/start surface; detailed job
  progress and cancellation controls remain primarily available through the
  API.
- Automated PDF generation is implemented; visual PDF review and production
  retention policies are not.
- The repository contains development SQLite files from local verification;
  production deployments should use a clean volume and configured environment.
