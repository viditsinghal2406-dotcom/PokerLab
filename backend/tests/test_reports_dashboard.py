from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_has_explicit_empty_state_and_report_exports():
    with TestClient(app) as client:
        dashboard = client.get("/api/v1/dashboard")
        assert dashboard.status_code == 200
        assert "experiments_count" in dashboard.json()

        experiment = client.post("/api/v1/experiments/run", json={
            "name": "report", "trials": 1, "hands": 2
        }).json()
        experiment_id = experiment["id"]
        html = client.get(f"/api/v1/experiments/{experiment_id}/report.html")
        assert html.status_code == 200
        assert "<!doctype html>" in html.text.lower()
        parquet = client.get(f"/api/v1/experiments/{experiment_id}/export.parquet")
        assert parquet.status_code == 200
        assert parquet.headers["content-type"].startswith("application/vnd.apache.parquet")
        pdf = client.get(f"/api/v1/experiments/{experiment_id}/report.pdf")
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")
