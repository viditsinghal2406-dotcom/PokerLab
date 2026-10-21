from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from statsmodels.tsa.arima.model import ARIMA

from app.analytics.atsa import holt, ses


@dataclass(frozen=True)
class ForecastMetrics:
    mae: float
    rmse: float
    mape: float | None
    bias: float
    residual_acf1: float


@dataclass(frozen=True)
class ForecastModelResult:
    name: str
    parameters: dict[str, float | int | str]
    forecast: list[float]
    metrics: ForecastMetrics


def _validate(values: list[float]) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or len(data) < 12 or not np.isfinite(data).all():
        raise ValueError("series must contain at least 12 finite numeric values")
    return data


def _metrics(actual: np.ndarray, forecast: np.ndarray) -> ForecastMetrics:
    residuals = actual - forecast
    denominator = float(np.sum((actual - actual.mean()) ** 2))
    centered = residuals - residuals.mean()
    acf1 = float(np.dot(centered[1:], centered[:-1]) / np.dot(centered, centered)) if len(residuals) > 1 and np.dot(centered, centered) else 0.0
    mape = float(np.mean(np.abs(residuals / actual)) * 100) if np.all(actual > 0) else None
    return ForecastMetrics(
        mae=float(np.mean(np.abs(residuals))),
        rmse=float(np.sqrt(np.mean(residuals ** 2))),
        mape=mape,
        bias=float(np.mean(residuals)),
        residual_acf1=acf1,
    )


def _tune_smoothing(train: np.ndarray, model: str) -> tuple[float, float]:
    best = (float("inf"), 0.5, 0.2)
    alphas = np.arange(0.1, 1.0, 0.1)
    betas = np.arange(0.1, 1.0, 0.1) if model == "Holt" else [0.0]
    for alpha in alphas:
        for beta in betas:
            fitted = np.asarray(
                ses(train.tolist(), float(alpha))
                if model == "SES"
                else holt(train.tolist(), float(alpha), float(beta))
            )
            score = float(np.mean(np.abs(train[1:] - fitted[:-1])))
            if score < best[0]:
                best = (score, float(alpha), float(beta))
    return best[1], best[2]


def _forecast(model: str, train: np.ndarray, horizon: int, window: int, order: tuple[int, int, int]) -> tuple[np.ndarray, dict]:
    if model == "Naive":
        return np.repeat(train[-1], horizon), {"method": "last value"}
    if model == "Moving avg":
        return np.repeat(train[-min(window, len(train)):].mean(), horizon), {"window": window}
    if model == "SES":
        alpha, _ = _tune_smoothing(train, "SES")
        fitted = ses(train.tolist(), alpha)
        return np.repeat(fitted[-1], horizon), {"alpha": alpha}
    if model == "Holt":
        alpha, beta = _tune_smoothing(train, "Holt")
        fitted = holt(train.tolist(), alpha, beta)
        trend = fitted[-1] - fitted[-2]
        return np.asarray([fitted[-1] + (index + 1) * trend for index in range(horizon)]), {"alpha": alpha, "beta": beta}
    if model == "Linear trend":
        coefficients = np.polyfit(np.arange(len(train)), train, 1)
        positions = np.arange(len(train), len(train) + horizon)
        return np.polyval(coefficients, positions), {"slope": float(coefficients[0])}
    if model == "ARIMA":
        fitted = ARIMA(train, order=order, trend="t" if order[1] else "c").fit()
        return np.asarray(fitted.forecast(horizon)), {"p": order[0], "d": order[1], "q": order[2]}
    raise ValueError(f"unsupported model: {model}")


def evaluate_forecasts(
    values: list[float],
    train_fraction: float = 0.8,
    models: list[str] | None = None,
    window: int = 5,
    order: tuple[int, int, int] = (1, 0, 0),
    rolling_origin: bool = False,
) -> list[ForecastModelResult]:
    data = _validate(values)
    if not 0.5 <= train_fraction < 1:
        raise ValueError("train_fraction must be at least 0.5 and below 1")
    cut = int(len(data) * train_fraction)
    if len(data) - cut < 2 or window < 1:
        raise ValueError("split must leave at least two test observations")
    selected = models or ["Naive", "Moving avg", "SES", "Holt", "Linear trend", "ARIMA"]
    results = []
    for name in selected:
        if rolling_origin:
            predictions = []
            actual = []
            for index in range(cut, len(data)):
                prediction, _ = _forecast(name, data[:index], 1, window, order)
                predictions.append(prediction[0])
                actual.append(data[index])
            forecast = np.asarray(predictions)
            target = np.asarray(actual)
        else:
            forecast, parameters = _forecast(name, data[:cut], len(data) - cut, window, order)
            target = data[cut:]
        _, parameters = _forecast(name, data[:cut], len(data) - cut, window, order)
        results.append(ForecastModelResult(name, parameters, forecast.tolist(), _metrics(target, forecast)))
    return results
