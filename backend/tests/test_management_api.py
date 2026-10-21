from fastapi.testclient import TestClient

from app.main import app


def test_experiment_and_strategy_management_endpoints():
    with TestClient(app) as client:
        strategy = client.post("/api/v1/strategy-configs", json={
            "name": "test preset", "policy": "vidit", "parameters": {"risk": 0.8}
        })
        assert strategy.status_code == 200
        config_id = strategy.json()["id"]
        assert any(item["id"] == config_id for item in client.get("/api/v1/strategy-configs").json())
        assert client.delete(f"/api/v1/strategy-configs/{config_id}").status_code == 204

        experiment = client.post("/api/v1/experiments/run", json={
            "name": "management", "trials": 1, "hands": 2
        }).json()
        assert any(item["id"] == experiment["id"] for item in client.get("/api/v1/experiments").json())
        assert client.delete(f"/api/v1/experiments/{experiment['id']}").status_code == 204
