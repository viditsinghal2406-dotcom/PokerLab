import numpy as np

from app.analytics.forecasting import evaluate_forecasts


def test_forecasting_uses_chronological_holdout_and_metrics() -> None:
    values = (np.arange(40, dtype=float) + np.sin(np.arange(40))).tolist()
    results = evaluate_forecasts(values, train_fraction=0.75, models=["Naive", "Linear trend"])
    assert len(results) == 2
    assert all(len(result.forecast) == 10 for result in results)
    assert all(result.metrics.mae >= 0 for result in results)


def test_mape_is_none_when_actuals_are_not_all_positive() -> None:
    values = list(np.linspace(-4, -1, 30))
    result = evaluate_forecasts(values, models=["Naive"])[0]
    assert result.metrics.mape is None


def test_rolling_origin_evaluation_returns_one_prediction_per_test_point() -> None:
    values = (np.arange(30, dtype=float) + 10).tolist()
    result = evaluate_forecasts(values, train_fraction=0.7, models=["Naive"], rolling_origin=True)[0]
    assert len(result.forecast) == 9
