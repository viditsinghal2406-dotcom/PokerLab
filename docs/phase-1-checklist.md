# Phase 1 checklist

## Prototype inspection

- [x] Read the single-file prototype and identify its major surfaces:
  poker engine, policies, ATSA, forecasting, experiments, profile.
- [x] Open `PokerLab.html` in a browser.
- [x] Click **Deal** once before porting.
- [x] Exercise the prototype table after fixing initialization; backend
  variant coverage is represented by engine tests.

## Bugs found before porting

- [x] **Deal/table initialization:** clicking **Deal** throws
  `TypeError: Cannot read properties of undefined (reading 'done')` in
  `drawT`. The hand loop invokes the UI render callback before `TG` is
  assigned by `nextHand`.
- [x] Betting-round termination: add a regression test for checks, raises,
  re-raises, and the three-raise cap.
- [x] All-in handling: add tests for partial calls, all-in raises, and street
  transitions.
- [x] Crazy Pineapple discard: add tests that exactly one card is discarded
  and that discarded cards cannot be used at showdown.
- [x] Add regression coverage for the prototype's renderer initialization bug.
- [ ] ADF critical values: replace hard-coded/approximate decisions with
  verified statistical-library output.
- [ ] PACF indexing: compare lags against a trusted implementation.
- [ ] Holt/SES parameter grids: test grid boundaries and short/constant series.

## Phase 1 implementation

- [x] Create the monorepo directories.
- [x] Add a FastAPI application and `/api/v1/health`.
- [x] Add a React/Vite/TypeScript shell that reads backend health.
- [x] Add initial backend and frontend tests.
- [x] Port the tested Phase 2 poker engine to `backend/app/simulation`.
- [ ] Add persistence, jobs, analytics, reports, and full playable UI.

## Phase 2 status

- [x] Port card representation, seeded deck, five-card evaluator, Hold'em
  best-hand selection, and Omaha exact-2+3 selection.
- [x] Add tested heads-up hand execution for folds, showdowns, pineapple
  discard, pot-limit bounds, deterministic seeds, and chip conservation.
- [x] Complete heads-up betting-round state transitions, all-in runouts, and
  multi-action street regression coverage.

Phase 2 is complete for the tested heads-up scope. Multiway players, side pots,
and additional variants are intentionally Phase 3 work.

## Phase 3 status

- [x] Add a tested 2-9 player Hold'em/Omaha dealing and showdown path.
- [x] Add rotating button, small-blind, and big-blind position metadata.
- [x] Add all-in contribution tracking, side-pot construction, folded-player
  eligibility, multiway payouts, and chip conservation.
- [x] Add Five-Card Draw with validated replacement-card selection.
- [x] Expose multiway Hold'em, Five-Card Draw, and Seven-Card Stud through
  validated REST endpoints.
- [x] Add a frontend multiway table control that displays backend board,
  winners, positions, and side pots.
- [x] Add a tested Seven-Card Stud deal/showdown path.
- [ ] Add interactive multiway betting actions beyond the current deterministic
  all-in/showdown simulation path.

## Phase 4 status

- [x] Port Vidit Mode, Aggressive, Balanced, Conservative, and Random policies.
- [x] Add adjustable aggression, bluff, and risk parameters with validation.
- [x] Add seeded, configurable Monte Carlo equity estimation with bounded cache.
- [x] Enforce policy visibility through a decision context containing only the
  acting player's cards, board, pot, and legal action bounds.
- [x] Expose policy decisions through `POST /api/v1/policies/decision`.
- [x] Integrate policy selection and adjustable Vidit parameters into the
  backend multiway simulation request and frontend table controls.
- [x] Return the selected policy's legal decision and estimated equity with
  each policy-enabled simulation.

## Phase 5 status

- [x] Add SQLite/SQLAlchemy persistence models for strategy configs,
  experiments, simulation runs, hands, model runs, forecast points, and notes.
- [x] Add reproducible background simulation jobs with seed, variant,
  player-count, progress, result, failure, and cancellation state.
- [x] Add resource limits and Pydantic validation for persisted strategy
  configs and simulation jobs.
- [x] Add job status, result, and cancellation endpoints under `/api/v1/jobs`.
- [ ] Add the full experiment/forecast persistence UI in later analytics phases.

## Phase 6 status

- [x] Add backend table sessions with legal actions, action validation, and
  backend-owned hand history.
- [x] Add playable frontend table controls with fold/check/call/raise actions
  and a betting slider.
- [x] Add showdown winner explanation and visible action history.
- [ ] Extend the table session from the current deterministic showdown path to
  full street-by-street multiway action orchestration.

## Phase 7 status

- [x] Add backend SMA, SES, Holt, ACF, and PACF primitives.
- [x] Replace the prototype AR-only approximation with statsmodels ARIMA(p,d,q).
- [x] Add AIC/BIC, residuals, Ljung-Box diagnostics, ADF, and KPSS.
- [x] Add forecast intervals and validated `POST /api/v1/analytics/atsa`.
- [x] Add the frontend ATSA visualization.
- [ ] Add saved analytics results.

## Phase 8 status

- [x] Add chronological Forecasting Arena evaluation with Naive, moving average,
  SES, Holt, linear trend, and ARIMA models.
- [x] Keep model fitting and parameter selection on the training split only.
- [x] Report MAE, RMSE, conditional MAPE, bias, and residual lag-1 ACF.
- [x] Add optional rolling-origin evaluation and `POST /api/v1/analytics/forecast`.
- [x] Add the frontend Forecasting Arena with real backend metrics, forecasts,
  charting, and the MAPE caveat.
- [ ] Add saved forecast runs and downloadable experiment records in a later
  persistence/reporting phase.

## Phase 9 status

- [x] Add reproducible Experiment Lab runs for experiment types A-F.
- [x] Use common trial seeds and configurable trial/hand limits.
- [x] Compare Vidit Mode against policies, tune Vidit parameters, and compare
  variants using backend policy decisions.
- [x] Report mean BB/hand, 95% confidence intervals, standard deviation,
  drawdown, and biggest observed win.
- [x] Persist experiment records in SQLite and provide CSV export.
- [x] Add the frontend Experiment Lab controls and results table.
- [ ] Add PDF reports and richer downloadable report packaging in Phase 10.

## Phase 10 status

- [x] Add a real-data dashboard summary endpoint with explicit empty states.
- [x] Add the frontend dashboard for experiment, job, and preset counts.
- [x] Add standalone HTML experiment reports.
- [x] Add CSV and Parquet experiment exports.
- [x] Add report/export API tests and frontend dashboard tests.
- [x] Add PDF rendering for saved experiment reports.
- [x] Add recent-condition summary data to the dashboard.

## Phase 11 status

### 11A: correctness and hardening

- [x] Add statsmodels-reference ADF/PACF regression tests and smoothing edge
  cases, including Hypothesis property tests.
- [x] Add shared street-by-street multiway betting state for 2-9 players with
  turn order, raise caps, all-in handling, pot-limit bounds, and showdown
  coverage for deterministic/property-tested action paths.
- [x] Make table sessions use the shared engine and hide opponent hole cards.
- [x] Persist ATSA/forecast runs with list/get/delete and available-series APIs.
- [x] Add frontend saved analytics history with delete controls.
- [x] Replace FastAPI startup events with lifespan and lazy-load frontend pages
  and charts.
- [ ] Complete full management UI for every persisted entity.

### 11B: product completeness

- [ ] Add 100,000-hand Simulation Lab presets, optional stopping, and richer
  trial controls.
- [ ] Complete ATSA lag-plot, differencing, and regression-residual views.
- [x] Show actual versus held-out predictions in the Forecasting Arena chart.
- [x] Add a local-only Vidit profile with personalization toggle, display name,
  Energy Mode, achievements, and easter egg control.
- [ ] Add bankroll chart series/range controls and tooltips.
- [ ] Run axe/Lighthouse and address remaining accessibility findings.

### 11C: deployment and verification

- [x] Add backend/frontend Dockerfiles, Compose healthchecks, and persistent
  SQLite/export volumes.
- [x] Run Docker Compose build/start and verify container health and HTTP
  responses.
- [x] Add and run an API workflow test from simulation job through report
  downloads.
- [x] Run frontend browser smoke workflow against the Docker stack (table,
  forecast, and experiment result rendering).
- [x] Measure simulation and analytics coverage.
- [x] Pin core backend dependencies and retain the frontend npm lockfile.
- [x] Expand README architecture, setup, API, methods, screenshots, and
  limitations documentation.
