import numpy as np
import pytest
from statsmodels.tsa.stattools import adfuller, pacf
from hypothesis import given, strategies as st

from app.analytics.atsa import correlations, holt, ses, stationarity


def test_adf_matches_statsmodels_on_random_walk_and_white_noise():
    for values in (
        np.cumsum(np.random.default_rng(11).normal(size=80)),
        np.random.default_rng(12).normal(size=80),
    ):
        expected = adfuller(values, maxlag=4, regression="c", autolag="AIC")
        actual = stationarity(values.tolist())["adf"]
        assert actual.statistic == pytest.approx(expected[0])
        assert actual.p_value == pytest.approx(expected[1])
        assert actual.lags == expected[2]


def test_adf_short_and_constant_series_fail_explicitly():
    with pytest.raises(ValueError):
        stationarity([1.0] * 7)
    with pytest.raises(ValueError):
        stationarity([1.0] * 20)


def test_pacf_matches_statsmodels_and_clamps_lag_index():
    values = np.random.default_rng(13).normal(size=100)
    expected = pacf(values, nlags=5, method="ywm")
    actual = correlations(values.tolist(), 5)["pacf"]
    assert actual == pytest.approx(expected)

    short = correlations(list(np.arange(8, dtype=float)), 99)["pacf"]
    assert len(short) == 4
    assert short[0] == pytest.approx(1.0)


@pytest.mark.parametrize("alpha", [0.0001, 1.0])
def test_ses_grid_boundaries_and_training_length(alpha):
    values = [1.0, 2.0, 3.0, 4.0]
    assert len(ses(values, alpha)) == len(values)
    with pytest.raises(ValueError):
        ses([1.0], alpha)


@pytest.mark.parametrize("alpha,beta", [(0.0001, 1.0), (1.0, 0.0001)])
def test_holt_grid_boundaries_and_constant_training(alpha, beta):
    values = [4.0] * 5
    assert len(holt(values, alpha, beta)) == len(values)
    with pytest.raises(ValueError):
        holt([1.0, 2.0], alpha, beta)


@given(st.lists(st.floats(-100, 100, allow_nan=False, allow_infinity=False), min_size=3, max_size=30))
def test_smoothing_never_changes_training_length(values):
    assert len(holt(values, 0.5, 0.5)) == len(values)
