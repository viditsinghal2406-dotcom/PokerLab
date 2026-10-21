import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HistoryPage } from "./HistoryPage";

describe("HistoryPage", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

  it("renders and deletes saved analytics runs", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({
        items: [{ id: 3, kind: "forecast", name: "Forecast evaluation", created_at: "2026-01-01" }],
      }), { status: 200 }))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<HistoryPage />);
    await waitFor(() => expect(screen.getByText(/Forecast evaluation/)).toBeTruthy());
    screen.getByRole("button", { name: "Delete Forecast evaluation" }).click();
    await waitFor(() => expect(screen.getByText(/No saved ATSA/)).toBeTruthy());
  });
});
