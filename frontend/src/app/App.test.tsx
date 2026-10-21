import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { BrowserRouter } from "react-router-dom";

import App from "./App";

describe("App", () => {
  afterEach(() => cleanup());

  it("renders the PokerLab shell", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      const body = url.endsWith("/health")
        ? { status: "ok", service: "pokerlab-api", version: "0.1.0" }
        : {
            id: "test-table", current_player: 0, street: "preflop", pot: 1.5,
            finished: false, board: [], hole: [["As", "Kd"]], winners: [],
            stacks: [99, 99, 98.5], action_log: ["Hand dealt by backend"],
            legal_actions: ["fold", "call", "raise", "all-in"],
            minimum_raise_to: 2, maximum_raise_to: 99,
          };
      return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
    });

    render(<BrowserRouter><App /></BrowserRouter>);

    expect(screen.getAllByRole("heading", { name: "PokerLab" }).length).toBeGreaterThan(0);
    expect((await screen.findByTestId("api-status")).textContent).toContain("API connected");
  });
});
