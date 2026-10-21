import time

from fastapi.testclient import TestClient

from app.main import app


def test_strategy_config_is_persisted() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/strategy-configs",
            json={"name": "Test Vidit", "policy": "vidit", "parameters": {"risk": 0.7}},
        )
    assert response.status_code == 200
    assert response.json()["parameters"] == {"risk": 0.7}


def test_simulation_job_reaches_terminal_state_with_progress() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/jobs/simulations",
            json={"seed": 12, "variant": "holdem", "player_count": 2, "hands": 3},
        )
        assert created.status_code == 202
        job_id = created.json()["id"]
        deadline = time.time() + 5
        while time.time() < deadline:
            status = client.get(f"/api/v1/jobs/simulations/{job_id}").json()
            if status["status"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(0.02)
        assert status["status"] == "completed"
        assert status["hands_completed"] == 3
        result = client.get(f"/api/v1/jobs/simulations/{job_id}/result")
        assert result.status_code == 200
        assert len(result.json()["results"]) == 3


def test_job_resource_limit_is_validated() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/jobs/simulations",
            json={"seed": 12, "variant": "holdem", "player_count": 2, "hands": 10001},
        )
    assert response.status_code == 422


def test_job_variant_is_validated_before_enqueueing() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/jobs/simulations",
            json={"seed": 12, "variant": "not-a-variant", "player_count": 2, "hands": 1},
        )
    assert response.status_code == 422
