from fastapi.testclient import TestClient

from app.main import app


def test_multiway_simulation_returns_selected_policy_decision() -> None:
    response = TestClient(app).post(
        "/api/v1/simulations/multiway",
        json={
            "seed": 77,
            "player_count": 3,
            "policy": "vidit",
            "aggression": 0.9,
            "bluff": 0.4,
            "risk": 0.8,
            "equity_samples": 8,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["policy"] == "vidit"
    assert body["decision"] in {"fold", "call", "check", "raise"}
    assert body["decision_equity"] is None or 0 <= body["decision_equity"] <= 1


def test_multiway_policy_rejects_unknown_policy() -> None:
    response = TestClient(app).post(
        "/api/v1/simulations/multiway",
        json={"seed": 1, "player_count": 2, "policy": "hidden-card-policy"},
    )
    assert response.status_code == 400
