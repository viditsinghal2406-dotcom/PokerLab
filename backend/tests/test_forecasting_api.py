import numpy as np
from fastapi.testclient import TestClient

from app.main import app


def test_forecast_api_returns_chronological_metrics() -> None:
    values = (np.arange(36, dtype=float) + 10).tolist()
    response = TestClient(app).post(
        "/api/v1/analytics/forecast",
        json={
            "values": values,
            "train_fraction": 0.75,
            "models": ["Naive", "Linear trend"],
            "rolling_origin": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["train_size"] == 27
    assert body["test_size"] == 9
    assert len(body["results"]) == 2
    assert len(body["results"][0]["forecast"]) == 9
    assert body["results"][0]["metrics"]["mape"] is not None
