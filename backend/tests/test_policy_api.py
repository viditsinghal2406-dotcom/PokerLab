from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_policy_api_accepts_only_acting_player_information() -> None:
    response = client.post(
        "/api/v1/policies/decision",
        json={
            "policy": "vidit",
            "hole": ["As", "Ah"],
            "board": ["Kd", "7c", "2s"],
            "pot": 10,
            "to_call": 2,
            "minimum_raise_to": 4,
            "maximum_raise_to": 20,
            "can_raise": True,
            "seed": 3,
            "samples": 8,
        },
    )
    assert response.status_code == 200
    assert response.json()["kind"] in {"fold", "call", "check", "raise"}


def test_policy_api_rejects_unknown_policy() -> None:
    response = client.post(
        "/api/v1/policies/decision",
        json={"policy": "opponent_cards", "hole": ["As", "Ah"], "pot": 1, "to_call": 0},
    )
    assert response.status_code == 400
