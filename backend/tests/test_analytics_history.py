from fastapi.testclient import TestClient

from app.main import app


def test_analytics_runs_are_saved_listed_read_and_deleted():
    with TestClient(app) as client:
        response = client.post("/api/v1/analytics/atsa", json={
            "values": [float(index) for index in range(20)],
            "order": [1, 1, 0],
            "horizon": 2,
            "lags": 3,
        })
        assert response.status_code == 200
        history = client.get("/api/v1/analytics/history")
        assert history.status_code == 200
        run_id = history.json()["items"][0]["id"]
        saved = client.get(f"/api/v1/analytics/history/{run_id}")
        assert saved.status_code == 200
        assert saved.json()["kind"] == "atsa"
        assert client.delete(f"/api/v1/analytics/history/{run_id}").status_code == 204
        assert client.get(f"/api/v1/analytics/history/{run_id}").status_code == 404
