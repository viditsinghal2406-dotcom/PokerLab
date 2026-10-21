export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export const apiBaseUrl = import.meta.env.VITE_API_URL ?? "/api/v1";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }

  return response.json() as Promise<HealthResponse>;
}

export type MultiwayResponse = {
  winners: number[];
  hole: string[][];
  board: string[];
  stacks: number[];
  contributions: number[];
  side_pots: { amount: number; cap: number; eligible: number[] }[];
  button: number;
  small_blind: number;
  big_blind: number;
  folded: number[];
  policy?: string | null;
  decision?: string | null;
  decision_amount?: number | null;
  decision_equity?: number | null;
};

export async function runMultiway(
  playerCount: number,
  policy: string,
  aggression: number,
  bluff: number,
  risk: number,
): Promise<MultiwayResponse> {
  const response = await fetch(`${apiBaseUrl}/simulations/multiway`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seed: Date.now() % 2 ** 32,
      player_count: playerCount,
      policy,
      aggression,
      bluff,
      risk,
    }),
  });
  if (!response.ok) throw new Error(`Simulation failed (${response.status})`);
  return response.json() as Promise<MultiwayResponse>;
}

export type TableState = {
  id: string;
  current_player: number;
  street: string;
  pot: number;
  finished: boolean;
  board: string[];
  hole: string[][];
  winners: number[];
  stacks: number[];
  action_log: string[];
  legal_actions: string[];
  minimum_raise_to: number;
  maximum_raise_to: number;
  to_call: number;
  pot_total: number;
  pot_breakdown: { amount: number; cap: number; eligible: number[] }[];
  seats: TableSeat[];
  events: TableEvent[];
  hand_names: Record<string, string>;
  best_five: Record<string, string[]>;
  used_cards: Record<string, string[]>;
  payouts: number[];
  won_uncontested: boolean;
};

export type TableSeat = {
  index: number;
  name: string;
  stack: number;
  current_bet: number;
  total_committed: number;
  folded: boolean;
  all_in: boolean;
  is_dealer: boolean;
  is_sb: boolean;
  is_bb: boolean;
  last_action: string | null;
  cards_visible: string[];
};

export type TableEvent = {
  seq: number;
  type: string;
  player: number | null;
  amount: number;
  total_bet: number;
  cards: string[];
  street: string;
  pot_after: number;
  stacks_after: number[];
  text: string;
};

export async function createTable(playerCount: number): Promise<TableState> {
  const response = await fetch(`${apiBaseUrl}/tables`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seed: Date.now() % 2 ** 32,
      player_count: playerCount,
      variant: "holdem",
    }),
  });
  if (!response.ok) throw new Error(`Table creation failed (${response.status})`);
  return response.json() as Promise<TableState>;
}

export async function submitTableAction(
  tableId: string,
  player: number,
  kind: string,
  amount = 0,
): Promise<TableState> {
  const response = await fetch(`${apiBaseUrl}/tables/${tableId}/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player, kind, amount }),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(detail?.detail ?? `Action failed (${response.status})`);
  }
  return response.json() as Promise<TableState>;
}

export type AtsaResponse = {
  adf: { statistic: number; p_value: number; lags: number; conclusion: string };
  kpss: { statistic: number; p_value: number; lags: number; conclusion: string };
  acf: number[];
  pacf: number[];
  arima_order: [number, number, number];
  aic: number;
  bic: number;
  forecast: number[];
  lower: number[];
  upper: number[];
  residuals: number[];
  ljung_box_p_value: number;
};

export async function runAtsa(
  values: number[],
  order: [number, number, number],
  horizon: number,
  lags: number,
): Promise<AtsaResponse> {
  const response = await fetch(`${apiBaseUrl}/analytics/atsa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ values, order, horizon, lags }),
  });
  if (!response.ok) throw new Error(`ATSA analysis failed (${response.status})`);
  return response.json() as Promise<AtsaResponse>;
}

export type ForecastResponse = {
  train_size: number;
  test_size: number;
  rolling_origin: boolean;
  actual: number[];
  results: {
    name: string;
    parameters: Record<string, number | string>;
    forecast: number[];
    metrics: {
      mae: number;
      rmse: number;
      mape: number | null;
      bias: number;
      residual_acf1: number;
    };
  }[];
};

export async function runForecast(
  values: number[],
  trainFraction: number,
  rollingOrigin: boolean,
): Promise<ForecastResponse> {
  const response = await fetch(`${apiBaseUrl}/analytics/forecast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      values,
      train_fraction: trainFraction,
      rolling_origin: rollingOrigin,
    }),
  });
  if (!response.ok) throw new Error(`Forecast analysis failed (${response.status})`);
  return response.json() as Promise<ForecastResponse>;
}

export type ExperimentResponse = {
  id: number;
  name: string;
  hypothesis: string;
  kind: string;
  variant: string;
  trials: number;
  hands: number;
  seeds: number[];
  metric: string;
  results: {
    label: string;
    mean_bb_per_hand: number;
    ci95: number | null;
    sd_bb_per_hand: number | null;
    average_max_drawdown: number;
    biggest_win: number;
    observations: number;
  }[];
};

export type DashboardResponse = {
  experiments_count: number;
  completed_jobs_count: number;
  strategy_configs_count: number;
  recent_experiments: { id: number; name: string; created_at: string }[];
  best_recent_condition: string | null;
  best_recent_mean_bb_per_hand: number | null;
};

export async function getDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${apiBaseUrl}/dashboard`);
  if (!response.ok) throw new Error(`Dashboard failed (${response.status})`);
  return response.json() as Promise<DashboardResponse>;
}

export type HistoryItem = { id: number; kind: string; name: string; created_at: string };

export async function runExperiment(
  name: string,
  hypothesis: string,
  kind: string,
  trials: number,
  hands: number,
): Promise<ExperimentResponse> {
  const response = await fetch(`${apiBaseUrl}/experiments/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, hypothesis, kind, trials, hands }),
  });
  if (!response.ok) throw new Error(`Experiment failed (${response.status})`);
  return response.json() as Promise<ExperimentResponse>;
}
