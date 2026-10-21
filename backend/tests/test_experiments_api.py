from fastapi.testclient import TestClient

from app.main import app


def test_experiment_api_persists_and_exports_csv():
    with TestClient(app) as client:
        response = client.post("/api/v1/experiments/run", json={
            "name": "api experiment", "kind": "E", "trials": 2, "hands": 3, "seed_start": 7
        })
        assert response.status_code == 200
        payload = response.json()
        assert payload["seeds"] == [7, 8]
        assert payload["results"][0]["ci95"] is not None
        saved = client.get(f"/api/v1/experiments/{payload['id']}")
        assert saved.status_code == 200
        exported = client.get(f"/api/v1/experiments/{payload['id']}/export.csv")
        assert exported.status_code == 200
        assert "mean_bb_per_hand" in exported.text
