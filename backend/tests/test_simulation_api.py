from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_multiway_api_returns_side_pots_and_positions() -> None:
    response = client.post(
        "/api/v1/simulations/multiway",
        json={"seed": 4, "player_count": 3, "stacks": [10, 25, 100], "all_in": [0, 1]},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["hole"]) == 3
    assert len(body["side_pots"]) == 3
    assert body["big_blind"] == 2


def test_simulation_api_validates_player_count() -> None:
    response = client.post(
        "/api/v1/simulations/multiway",
        json={"seed": 4, "player_count": 10},
    )
    assert response.status_code == 422


def test_draw_api_returns_five_card_hands() -> None:
    response = client.post(
        "/api/v1/simulations/draw",
        json={"seed": 9, "draw_indices": [[0, 1], []]},
    )
    assert response.status_code == 200
    assert all(len(hand) == 5 for hand in response.json()["hole"])


def test_stud_api_returns_seven_card_hands() -> None:
    response = client.post(
        "/api/v1/simulations/stud",
        json={"seed": 10, "player_count": 3},
    )
    assert response.status_code == 200
    assert all(len(hand) == 7 for hand in response.json()["hole"])
