import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DashboardPage } from "./DashboardPage";

describe("DashboardPage", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows an empty state from real dashboard data", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      experiments_count: 0, completed_jobs_count: 0, strategy_configs_count: 0,
      recent_experiments: [], best_recent_condition: null, best_recent_mean_bb_per_hand: null,
    }), { status: 200 })));
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText(/No experiments yet/)).toBeTruthy());
    expect(screen.getByText("Experiments: 0")).toBeTruthy();
  });
});
