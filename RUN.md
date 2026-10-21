# Running PokerLab

This guide covers Windows PowerShell local development, tests, browser tests,
and Docker. Run commands from the repository root:

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs
```

## Prerequisites

- Python 3.11 or newer
- Node.js 22 or newer
- npm
- Docker Desktop (optional, for the container workflow)

The local Python environment is named `pokerlabs` and is expected at
`.\pokerlabs`.

## First-time local setup

### 1. Create or activate the Python environment

If the environment does not exist:

```powershell
py -3.11 -m venv pokerlabs
```

Activate it:

```powershell
.\pokerlabs\Scripts\Activate.ps1
```

If PowerShell blocks activation, run Python through the environment directly:

```powershell
& .\pokerlabs\Scripts\python.exe --version
```

Install backend dependencies:

```powershell
& .\pokerlabs\Scripts\python.exe -m pip install --upgrade pip
& .\pokerlabs\Scripts\python.exe -m pip install -r backend\requirements.txt
```

The root [requirements.txt](requirements.txt) delegates to the backend
manifest. The pinned environment snapshot is
[backend/requirements.lock.txt](backend/requirements.lock.txt).

### 2. Install frontend dependencies

```powershell
Set-Location frontend
npm.cmd ci
Set-Location ..
```

Use `npm.cmd` in PowerShell if the local execution policy prevents
`npm.ps1`.

## Start the local application

Open two PowerShell windows.

### Window 1: backend

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs\backend
& ..\pokerlabs\Scripts\python.exe -m uvicorn app.main:app `
  --host 127.0.0.1 --port 8001 --reload
```

Backend URLs:

- Health: <http://127.0.0.1:8001/api/v1/health>
- Swagger UI: <http://127.0.0.1:8001/docs>
- OpenAPI JSON: <http://127.0.0.1:8001/openapi.json>

### Window 2: frontend

```powershell
Set-Location C:\Users\vidit\Desktop\PokerLabs\frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5174
```

Open <http://127.0.0.1:5174>.

The Vite `/api` proxy forwards to `http://127.0.0.1:8001`. If you use the
default Vite port instead, start with `npm.cmd run dev` and open
<http://127.0.0.1:5173>; the API proxy still targets port 8001.

Stop either server with `Ctrl+C`. Do not leave development servers running
when they are not needed.

## Local environment variables

Copy the example file when you need custom configuration:

```powershell
Copy-Item .env.example .env
```

Important values:

```text
DATABASE_URL=sqlite:///./pokerlab.db
VITE_API_URL=
```

An empty `VITE_API_URL` uses the Vite proxy during local development. The
backend currently reads its database configuration from the environment used
by the application; for normal local use, the default SQLite file is enough.

## Test and build commands

### Backend tests

```powershell
& .\pokerlabs\Scripts\python.exe -m pytest backend
```

With coverage for the simulation and analytics packages:

```powershell
& .\pokerlabs\Scripts\python.exe -m pytest backend `
  --cov=backend/app/simulation `
  --cov=backend/app/analytics `
  --cov-report=term-missing
```

### Frontend unit tests

```powershell
Set-Location frontend
npm.cmd test -- --run
```

### Frontend type-check and production build

```powershell
npm.cmd run build
```

### Playwright browser tests

Install the browser once:

```powershell
npx.cmd playwright install chromium
```

Start the backend and frontend first, then run:

```powershell
npm.cmd run test:e2e -- --reporter=line
```

The browser suite covers:

- Complete hand flow
- Preflop, flop and showdown screenshots
- All-in screenshots
- Desktop and mobile viewports
- 2–9 seat responsive geometry
- Horizontal-overflow checks

Screenshots and traces are written under `frontend\test-results`.

## Docker workflow

Make sure Docker Desktop is running, then from the repository root:

```powershell
docker compose up --build
```

Open:

- Frontend: <http://127.0.0.1:5174>
- API health: <http://127.0.0.1:8001/api/v1/health>
- API docs: <http://127.0.0.1:8001/docs>

Docker Compose creates persistent volumes for:

- SQLite data: `pokerlab-data`
- Exports: `pokerlab-exports`

Stop the stack:

```powershell
docker compose down
```

Stop it and remove persisted volumes:

```powershell
docker compose down -v
```

The last command deletes the Docker-managed database and exports. Use it only
when you intentionally want a clean data store.

## Useful workflow checks

1. Start the backend and confirm `/api/v1/health` returns status `ok`.
2. Start the frontend and confirm the shell says `API connected`.
3. Open `/arena`, create a hand, and verify the opponent cards remain backs
   until showdown.
4. Run a simulation from `/lab`, poll its result, and inspect the dashboard.
5. Run ATSA or Forecasting with a comma-separated series.
6. Run an Experiment Lab comparison and open its saved record/export.
7. Run both frontend and backend tests before submitting changes.

## Common problems

### API unavailable in the frontend

Confirm that the backend is running on port 8001. The local Vite proxy is
configured for that port.

### `npm` cannot run in PowerShell

Use `npm.cmd` instead of `npm`.

### PowerShell refuses environment activation

Use the environment's executable directly:

```powershell
& .\pokerlabs\Scripts\python.exe -m pytest backend
```

### Port already in use

Use different ports and provide a matching API URL, or stop the process that
owns the port. The documented defaults are backend `8001` and frontend `5174`.

## Project entry points

- Backend app: [backend/app/main.py](backend/app/main.py)
- Backend routes: [backend/app/api/router.py](backend/app/api/router.py)
- Frontend entry: [frontend/src/main.tsx](frontend/src/main.tsx)
- Frontend routes and shell: [frontend/src/app/App.tsx](frontend/src/app/App.tsx)
- Frontend API client: [frontend/src/services/api.ts](frontend/src/services/api.ts)
- Frontend browser tests: [frontend/e2e/poker-arena.spec.ts](frontend/e2e/poker-arena.spec.ts)
