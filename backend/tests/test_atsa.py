import numpy as np

from app.analytics.atsa import arima, correlations, holt, sma, stationarity


def test_sma_and_holt_validate_and_preserve_length() -> None:
    values = [float(index) for index in range(20)]
    assert len(sma(values, 4)) == 20
    assert len(holt(values, 0.5, 0.2)) == 20


def test_stationarity_exposes_adf_and_kpss() -> None:
    rng = np.random.default_rng(4)
    result = stationarity(rng.normal(size=100).tolist())
    assert result["adf"].p_value < 0.05
    assert result["kpss"].conclusion == "stationary"


def test_arima_is_true_arima_with_information_criteria_and_intervals() -> None:
    values = np.cumsum(np.random.default_rng(5).normal(size=80)).tolist()
    result = arima(values, (1, 1, 1), 6)
    assert result.order == (1, 1, 1)
    assert np.isfinite(result.aic)
    assert np.isfinite(result.bic)
    assert len(result.forecast) == len(result.lower) == len(result.upper) == 6
    assert result.ljung_box_p_value >= 0


def test_acf_pacf_have_aligned_lags() -> None:
    result = correlations(list(range(30)), 5)
    assert len(result["acf"]) == len(result["pacf"]) == 6
