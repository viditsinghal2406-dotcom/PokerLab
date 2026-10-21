from fastapi.testclient import TestClient

from app.main import app


def test_atsa_api_returns_arima_diagnostics_and_intervals() -> None:
    values = [float(index) + (index % 3) * 0.1 for index in range(40)]
    response = TestClient(app).post(
        "/api/v1/analytics/atsa",
        json={"values": values, "order": [1, 0, 1], "horizon": 4, "lags": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["arima_order"] == [1, 0, 1]
    assert len(body["forecast"]) == len(body["lower"]) == len(body["upper"]) == 4
    assert len(body["acf"]) == len(body["pacf"]) == 5
