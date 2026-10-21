# PokerLab Project Handoff

Last updated: 2026-10-21

## Repository status

- Repository root: `C:\Users\vidit\Desktop\PokerLabs`
- Git status: **not available**. The directory is not a Git repository; both
  `git branch --show-current` and `git status --short` returned
  `fatal: not a git repository`.
- Current branch: **unknown**, because no `.git` directory exists.
- No code changes were discarded. Generated caches, local databases, build
  output, and temporary environments were removed.

## Architecture and stack

```text
React + Vite + TypeScript browser
        |
        | /api proxy or VITE_API_URL
        v
FastAPI /api/v1
        |
        +-- Python poker simulation and betting engine
        +-- policies and Monte Carlo equity
        +-- ATSA/forecasting analytics
        +-- SQLAlchemy + SQLite persistence
        +-- HTML/PDF/CSV/Parquet reports
```

Frontend:

- React 18, TypeScript, Vite
- React Router
- Recharts
- Lucide icons
- Framer Motion dependency is installed but is not required by the current
  table implementation
- Self-hosted Plus Jakarta Sans and Cormorant Garamond
- CSS design tokens and component styles; Tailwind is **not** installed
- Vitest, React Testing Library, Playwright

Backend:

- Python 3.11+
- FastAPI, Pydantic, Uvicorn
- SQLAlchemy, SQLite, aiosqlite
- NumPy, pandas, SciPy, statsmodels, scikit-learn
- ReportLab and PyArrow
- pytest, pytest-cov, Hypothesis

Important entry points:

- Backend app: `backend/app/main.py`
- Backend routes: `backend/app/api/router.py`
- Poker engine: `backend/app/simulation/`
- Frontend entry: `frontend/src/main.tsx`
- Frontend shell/routes: `frontend/src/app/App.tsx`
- Frontend API client: `frontend/src/services/api.ts`
- Poker page: `frontend/src/pages/PokerArenaPage.tsx`
- Browser tests: `frontend/e2e/poker-arena.spec.ts`

## Files changed in this session

### Poker Arena and frontend behavior

- `frontend/src/services/api.ts`
- `frontend/src/components/poker/seatLayout.ts`
- `frontend/src/components/poker/Seat.tsx`
- `frontend/src/components/poker/TableLayout.tsx`
- `frontend/src/components/poker/ChipStack.tsx`
- `frontend/src/components/poker/PlayingCard.tsx`
- `frontend/src/components/poker/CardBack.tsx`
- `frontend/src/components/poker/Board.tsx`
- `frontend/src/components/poker/ShowdownPanel.tsx`
- `frontend/src/components/poker/PokerArena.test.tsx`
- `frontend/src/pages/PokerArenaPage.tsx`
- `frontend/src/styles.css`

### Application shell and visual design

- `frontend/src/styles/tokens.css`
- `frontend/src/app/App.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/SimulationLabPage.tsx`
- `frontend/src/pages/AtsaPage.tsx`
- `frontend/src/pages/ForecastPage.tsx`
- `frontend/src/pages/ExperimentsPage.tsx`
- `frontend/src/pages/HistoryPage.tsx`
- `frontend/src/pages/ProfilePage.tsx`
- `frontend/vitest.config.ts`

### Browser testing

- `frontend/e2e/poker-arena.spec.ts`
- `frontend/playwright.config.ts`
- `frontend/package.json`
- `frontend/package-lock.json`

### Documentation and repository hygiene

- `README.md`
- `RUN.md`
- `.gitignore`
- `.dockerignore`

Earlier backend work in this project also includes the typed table-event and
seat contracts, event serialization, hidden-card privacy, showdown metadata,
multiway engine, analytics, persistence, jobs, reports, and their tests under
`backend/app/` and `backend/tests/`. Those files were not changed in the final
visual/documentation pass.

## Completed work

- FastAPI backend with health endpoint and API documentation.
- React/Vite routed frontend with dashboard, arena, lab, ATSA, forecasting,
  experiments, profile, and history surfaces.
- Backend-authoritative poker table state and legal actions.
- 2–9 player table support, blinds, multiway state, all-ins, side pots, and
  showdown data.
- Hidden opponent cards before showdown.
- Typed table events, authoritative seat metadata, pot breakdown, `to_call`,
  payouts, hand names, and best-five/used-card fields.
- SVG-style rank/suit card rendering and green card backs.
- Responsive polar seat layout with 2–9 seat rendering.
- Premium dark/graphite research UI styling and poker-room table styling.
- Dashboard and analytics page visual hierarchy improvements.
- Local-only profile personalization behavior retained.
- Dockerfiles, Compose healthchecks, persistent SQLite/export volumes.
- Windows-oriented [RUN.md](RUN.md) and updated [README.md](README.md).
- Generated caches, local databases, temporary environments, build output, and
  Playwright result output cleaned from the workspace.

## Verified results

These commands were actually executed successfully during this session:

Backend:

```text
66 passed, 5 warnings
```

Frontend unit tests:

```text
7 test files passed
14 tests passed
```

Frontend production build:

```text
TypeScript compilation passed
Vite production build passed
```

Playwright before the final visual/documentation-only cleanup:

```text
3 tests passed
```

Those browser tests covered complete hand flow, desktop/mobile screenshots,
all-in resolution, 2–9 seat geometry, and horizontal-overflow checks.

Browser smoke checks also verified the backend-connected arena and mobile
dashboard with no horizontal overflow at the checked viewports.

Not verified in the final state:

- `docker compose up --build` was not executed in the final cleanup pass.
- No Git diff/status can be reported because this folder has no Git metadata.
- Full Playwright rerun after the final documentation/cleanup changes was not
  necessary for those non-runtime changes and was not repeated.
- No production deployment or HTTPS/reverse-proxy deployment was performed.

Known warnings:

- Backend tests emit five statsmodels warnings involving singular matrices and
  the future `adfuller` return shape. These were observed, not suppressed.
- npm audit previously reported 3 moderate, 1 high, and 2 critical findings.
  No forced audit fix was applied.

## Outstanding issues

### 1. Poker Arena seat-overlap bug

The arena uses percentage-based polar seat coordinates and absolute-positioned
seat cards. This prevents the previous fixed seat-class problem, but it is not
yet collision-aware. At some combinations of player count, narrow viewport,
seat content height, and table size:

- Seats can approach or overlap the central board/pot region.
- Neighboring compact seats can become visually crowded.
- Long names, status badges, or larger stack labels can exceed the calculated
  seat footprint.

The next fix should measure actual seat bounds and use collision-safe layout
zones or a responsive ring/grid fallback for 6–9 players, especially at
390×844 and 768×1024.

### 2. Playing-card rank/suit readability

Cards now use SVG rank, suit, and pip content, but readability still needs a
polish pass:

- Small seat cards use very compact SVG text.
- Dense pip layouts are functional but not yet as legible as a production
  poker-client card face.
- The browser accessibility tree exposes the SVG internals beneath the card
  image role, which is noisy even though the card has a usable accessible name.
- Face-card artwork is currently represented by a central suit rather than
  illustrated face designs.

The next fix should use explicit SVG `<title>`/`<desc>` content, stronger
responsive card sizing, and tuned pip/rank positioning for seat cards.

### Other known limitations

- Local `.env.example` still shows `API_PORT=8000`, while the documented local
  backend workflow uses port `8001`; the explicit commands are correct, but
  this variable should be reconciled.
- Simulation Lab is currently a configuration/start surface; detailed job
  progress and cancellation are more complete at the API level.
- SQLite is suitable for local/single-machine use, not a multi-instance public
  deployment.
- Authentication, authorization, rate limiting, production CORS policy,
  monitoring, and automated backups are not complete.
- Optional stopping rules, multiple independent trial controls, and bankroll
  moving-average charts remain incomplete.

## Docker Compose and URLs

`docker-compose.yml` defines:

- Backend container built from `backend/Dockerfile`
- Frontend container built from `frontend/Dockerfile`
- Backend host port `8001` mapped to container port `8000`
- Frontend host port `5174` mapped to container port `80`
- Backend healthcheck at `/api/v1/health`
- Persistent volumes `pokerlab-data` and `pokerlab-exports`

Docker URLs:

- Frontend: `http://127.0.0.1:5174`
- API health: `http://127.0.0.1:8001/api/v1/health`
- Swagger: `http://127.0.0.1:8001/docs`
- OpenAPI: `http://127.0.0.1:8001/openapi.json`

## Exact local commands

From PowerShell:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs
```

Create the environment if needed:

```powershell
py -3.11 -m venv pokerlabs
```

Install dependencies:

```powershell
& .\pokerlabs\Scripts\python.exe -m pip install --upgrade pip
& .\pokerlabs\Scripts\python.exe -m pip install -r backend\requirements.txt
Set-Location frontend
npm.cmd ci
Set-Location ..
```

Start the backend in PowerShell window 1:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs\backend
& ..\pokerlabs\Scripts\python.exe -m uvicorn app.main:app `
  --host 127.0.0.1 --port 8001 --reload
```

Start the frontend in PowerShell window 2:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs\frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5174
```

Run tests:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs
& .\pokerlabs\Scripts\python.exe -m pytest backend
Set-Location frontend
npm.cmd test -- --run
npm.cmd run build
```

Run browser tests after both servers are running:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs\frontend
npx.cmd playwright install chromium
npm.cmd run test:e2e -- --reporter=line
```

Run Docker:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs
docker compose up --build
```

## Next five recommended tasks

1. **Fix collision-safe arena geometry.** Add automated bounding-box assertions
   for every supported player count at 390, 768, 1280, and 1920 widths, then
   implement a ring/grid fallback for crowded multiway tables.
2. **Polish card readability.** Improve SVG title/description semantics, pip
   placement, face-card treatment, and minimum card sizing in compact seats.
3. **Reconcile environment and deployment configuration.** Align
   `.env.example` port values with the documented `8001` workflow, tighten
   production CORS, and run `docker compose up --build` from a clean state.
4. **Complete Simulation Lab operations.** Add frontend polling, progress,
   elapsed time, cancellation, result presentation, and repeat-with-seed
   controls using the existing jobs API.
5. **Harden production readiness.** Add authentication/session isolation,
   rate/resource limits, structured logging, backup/restore procedures,
   dependency security review, and migrate persistence from SQLite if deploying
   multiple backend instances.
