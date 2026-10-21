import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ExperimentsPage } from "./ExperimentsPage";

describe("ExperimentsPage", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("renders persisted experiment metrics", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      id: 4, name: "PokerLab experiment", hypothesis: "", kind: "E", variant: "holdem",
      trials: 2, hands: 3, seeds: [1000, 1001], metric: "profit per hand in BB",
      results: [{ label: "Vidit", mean_bb_per_hand: 0.2, ci95: 0.1, sd_bb_per_hand: 0.08,
        average_max_drawdown: 1, biggest_win: 2, observations: 6 }],
    }), { status: 200 })));
    render(<ExperimentsPage />);
    fireEvent.click(screen.getByRole("button", { name: "Run experiment" }));
    await waitFor(() => expect(screen.getByText("Vidit")).toBeTruthy());
    expect(screen.getByText(/Common seeds: 1000, 1001/)).toBeTruthy();
  });
});
