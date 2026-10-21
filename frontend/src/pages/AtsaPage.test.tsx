import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AtsaPage } from "./AtsaPage";

describe("AtsaPage", () => {
  class ResizeObserverStub {
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });
  it("validates short series before making a request", () => {
    render(<AtsaPage />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "1,2,3" } });
    fireEvent.click(screen.getByRole("button", { name: "Run ATSA" }));
    expect(screen.getByText("Enter at least 8 comma-separated numeric values.")).toBeTruthy();
  });

  it("renders diagnostics and charts from the backend result", async () => {
    vi.stubGlobal("ResizeObserver", ResizeObserverStub);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      adf: { statistic: -3, p_value: 0.01, lags: 2, conclusion: "stationary" },
      kpss: { statistic: 0.1, p_value: 0.1, lags: 2, conclusion: "stationary" },
      acf: [1, 0.2], pacf: [1, 0.1], arima_order: [1, 0, 1],
      aic: 10, bic: 12, forecast: [1, 2], lower: [0, 1], upper: [2, 3],
      residuals: [0.1, -0.1], ljung_box_p_value: 0.4,
    }), { status: 200 })));
    render(<AtsaPage />);
    fireEvent.click(screen.getAllByRole("button", { name: "Run ATSA" })[0]);
    await waitFor(() => expect(screen.getByText(/ARIMA\(1,0,1\)/)).toBeTruthy());
    expect(screen.getByRole("img", { name: "Forecast with intervals" })).toBeTruthy();
    expect(screen.getByRole("img", { name: "ACF" })).toBeTruthy();
  });
});
