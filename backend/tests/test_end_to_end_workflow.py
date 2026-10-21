import time

from fastapi.testclient import TestClient

from app.main import app


def test_api_workflow_from_job_to_reports():
    with TestClient(app) as client:
        job = client.post("/api/v1/jobs/simulations", json={
            "seed": 44, "variant": "holdem", "player_count": 3, "hands": 2
        })
        assert job.status_code == 202
        job_id = job.json()["id"]
        for _ in range(50):
            status = client.get(f"/api/v1/jobs/simulations/{job_id}").json()
            if status["status"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(0.02)
        assert status["status"] == "completed"

        values = [float(index) for index in range(20)]
        assert client.get("/api/v1/analytics/series").status_code == 200
        assert client.post("/api/v1/analytics/atsa", json={
            "values": values, "order": [1, 1, 0], "horizon": 2, "lags": 3
        }).status_code == 200
        assert client.post("/api/v1/analytics/forecast", json={
            "values": values, "models": ["Naive"], "train_fraction": 0.8
        }).status_code == 200
        experiment = client.post("/api/v1/experiments/run", json={
            "name": "workflow", "trials": 1, "hands": 2
        })
        assert experiment.status_code == 200
        experiment_id = experiment.json()["id"]
        for suffix in ("report.html", "report.pdf", "export.csv", "export.parquet"):
            assert client.get(f"/api/v1/experiments/{experiment_id}/{suffix}").status_code == 200
