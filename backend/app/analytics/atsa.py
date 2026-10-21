from __future__ import annotations

from dataclasses import dataclass
import warnings

import numpy as np
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, kpss, pacf
from statsmodels.tools.sm_exceptions import (
    EstimationWarning,
    InterpolationWarning,
    SingularMatrixWarning,
    ValueWarning,
)


@dataclass(frozen=True)
class Diagnostic:
    statistic: float
    p_value: float
    lags: int
    conclusion: str


@dataclass(frozen=True)
class ArimaResult:
    order: tuple[int, int, int]
    aic: float
    bic: float
    coefficients: list[float]
    fitted: list[float]
    residuals: list[float]
    forecast: list[float]
    lower: list[float]
    upper: list[float]
    ljung_box_p_value: float


def _series(values: list[float]) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or len(data) < 8 or not np.isfinite(data).all():
        raise ValueError("series must contain at least 8 finite numeric values")
    return data


def sma(values: list[float], window: int) -> list[float | None]:
    data = _series(values)
    if window < 1 or window > len(data):
        raise ValueError("window must fit within the series")
    return [None if index + 1 < window else float(data[index - window + 1:index + 1].mean())
            for index in range(len(data))]


def ses(values: list[float], alpha: float) -> list[float]:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or len(data) < 2 or not np.isfinite(data).all():
        raise ValueError("SES requires at least 2 finite numeric values")
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be greater than 0 and at most 1")
    level = float(data[0])
    forecasts = [level]
    for value in data[1:]:
        forecasts.append(level)
        level = alpha * float(value) + (1 - alpha) * level
    return forecasts


def holt(values: list[float], alpha: float, beta: float) -> list[float]:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or len(data) < 3 or not np.isfinite(data).all():
        raise ValueError("Holt requires at least 3 finite numeric values")
    if not 0 < alpha <= 1 or not 0 < beta <= 1:
        raise ValueError("alpha and beta must be greater than 0 and at most 1")
    level, trend = float(data[0]), float(data[1] - data[0])
    forecasts = [level]
    for value in data[1:]:
        previous = level
        forecasts.append(level + trend)
        level = alpha * float(value) + (1 - alpha) * (level + trend)
        trend = beta * (level - previous) + (1 - beta) * trend
    return forecasts


def select_adf_lag(values: list[float], max_lag: int = 8) -> int:
    data = _series(values)
    return min(max_lag, max(0, int(len(data) ** (1 / 3))))


def stationarity(values: list[float]) -> dict[str, Diagnostic]:
    data = _series(values)
    if np.ptp(data) == 0:
        raise ValueError("stationarity tests require a non-constant series")
    adf_lag = select_adf_lag(values)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, module="statsmodels")
        warnings.filterwarnings("ignore", category=InterpolationWarning)
        warnings.filterwarnings("ignore", message="adfuller currently returns")
        warnings.filterwarnings("ignore", message="kpss currently returns")
        adf_result = adfuller(data, maxlag=adf_lag, regression="c", autolag="AIC")
        kpss_result = kpss(data, regression="c", nlags="auto")
    return {
        "adf": Diagnostic(
            float(adf_result[0]), float(adf_result[1]), int(adf_result[2]),
            "stationary" if adf_result[1] < 0.05 else "unit root not rejected",
        ),
        "kpss": Diagnostic(
            float(kpss_result[0]), float(kpss_result[1]), int(kpss_result[2]),
            "stationary" if kpss_result[1] >= 0.05 else "stationarity rejected",
        ),
    }


def arima(
    values: list[float],
    order: tuple[int, int, int],
    horizon: int,
) -> ArimaResult:
    data = _series(values)
    p, d, q = order
    if min(p, d, q) < 0 or max(p, d, q) > 5 or horizon < 1 or horizon > 1000:
        raise ValueError("ARIMA orders must be 0..5 and horizon must be 1..1000")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ValueWarning)
        warnings.filterwarnings("ignore", category=SingularMatrixWarning)
        warnings.filterwarnings("ignore", category=EstimationWarning)
        warnings.filterwarnings("ignore", message="The design matrix is rank-deficient")
        fitted_model = ARIMA(data, order=order, trend="t" if d else "c").fit()
        prediction = fitted_model.get_forecast(steps=horizon)
        interval = prediction.conf_int()
        residuals = np.asarray(fitted_model.resid, dtype=float)
        lag = min(10, max(1, len(residuals) // 5))
        ljung = acorr_ljungbox(residuals, lags=[lag], return_df=True)
    return ArimaResult(
        order=order,
        aic=float(fitted_model.aic),
        bic=float(fitted_model.bic),
        coefficients=[float(value) for value in fitted_model.params],
        fitted=[float(value) for value in fitted_model.fittedvalues],
        residuals=residuals.tolist(),
        forecast=[float(value) for value in prediction.predicted_mean],
        lower=[float(value) for value in interval[:, 0]],
        upper=[float(value) for value in interval[:, 1]],
        ljung_box_p_value=float(ljung["lb_pvalue"].iloc[0]),
    )


def correlations(values: list[float], lags: int) -> dict[str, list[float]]:
    data = _series(values)
    if lags < 1:
        raise ValueError("lags must be positive")
    effective_lags = min(lags, max(1, (len(data) - 1) // 2))
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The design matrix is rank-deficient")
        return {
            "acf": acf(data, nlags=effective_lags).tolist(),
            "pacf": pacf(data, nlags=effective_lags, method="ywm").tolist(),
        }
