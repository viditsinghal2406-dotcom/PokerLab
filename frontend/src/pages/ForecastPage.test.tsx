import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ForecastPage } from "./ForecastPage";

describe("ForecastPage", () => {
  class ResizeObserverStub {
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("validates a short series", () => {
    render(<ForecastPage />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "1,2,3" } });
    fireEvent.click(screen.getByRole("button", { name: "Run Forecast Arena" }));
    expect(screen.getByText("Enter at least 12 comma-separated numeric values.")).toBeTruthy();
  });

  it("renders real backend model metrics", async () => {
    vi.stubGlobal("ResizeObserver", ResizeObserverStub);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      train_size: 10, test_size: 3, rolling_origin: false,
      results: [{ name: "Naive", parameters: {}, forecast: [1, 2, 3],
        metrics: { mae: 1, rmse: 1.2, mape: null, bias: 0.1, residual_acf1: 0.2 } }],
    }), { status: 200 })));
    render(<ForecastPage />);
    fireEvent.click(screen.getByRole("button", { name: "Run Forecast Arena" }));
    await waitFor(() => expect(screen.getByText("Naive")).toBeTruthy());
    expect(screen.getByText("n/a")).toBeTruthy();
  });
});
