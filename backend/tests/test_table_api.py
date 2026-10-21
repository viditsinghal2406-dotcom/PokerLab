from fastapi.testclient import TestClient

from app.main import app


def test_playable_table_exposes_legal_actions_and_history() -> None:
    with TestClient(app) as client:
        created = client.post("/api/v1/tables", json={"seed": 4, "player_count": 3})
        assert created.status_code == 200
        table = created.json()
        assert table["legal_actions"] == ["fold", "call", "raise", "all-in"]
        assert table["action_log"] == ["Hand dealt by backend"]
        action = client.post(
            f"/api/v1/tables/{table['id']}/actions",
            json={"player": 0, "kind": "call"},
        )
        assert action.status_code == 200
        assert len(action.json()["action_log"]) > 1
        assert len(action.json()["hole"]) == 1


def test_playable_table_rejects_wrong_player_and_invalid_raise() -> None:
    with TestClient(app) as client:
        table = client.post("/api/v1/tables", json={"seed": 5, "player_count": 2}).json()
        wrong_player = client.post(
            f"/api/v1/tables/{table['id']}/actions",
            json={"player": 1, "kind": "check"},
        )
        assert wrong_player.status_code == 409
        invalid_raise = client.post(
            f"/api/v1/tables/{table['id']}/actions",
            json={"player": 0, "kind": "raise", "amount": 0},
        )
        assert invalid_raise.status_code == 409
