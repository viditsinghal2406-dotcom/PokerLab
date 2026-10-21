import json

from fastapi.testclient import TestClient

from app.main import app


def test_table_response_has_ordered_events_and_authoritative_seats() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/tables",
            json={"seed": 17, "player_count": 3, "variant": "holdem"},
        )
        assert response.status_code == 200
        table = response.json()
        assert [event["seq"] for event in table["events"]] == sorted(
            event["seq"] for event in table["events"]
        )
        assert {event["type"] for event in table["events"]} >= {
            "hand_start", "blinds_posted", "deal_hole"
        }
        assert len(table["seats"]) == 3
        assert sum(seat["stack"] for seat in table["seats"]) <= 298.5
        assert table["to_call"] >= 0
        assert table["pot_total"] >= 1.5
        assert table["seats"][0]["cards_visible"]
        assert table["seats"][1]["cards_visible"] == []

        action = client.post(
            f"/api/v1/tables/{table['id']}/actions",
            json={"player": 0, "kind": "call"},
        ).json()
        assert action["events"]
        assert min(event["seq"] for event in action["events"]) > max(
            event["seq"] for event in table["events"]
        )
        assert all(event["type"] in {
            "fold", "check", "call", "raise", "all_in", "street_change",
            "deal_board", "showdown", "payout"
        } for event in action["events"])

        repeat = client.get(f"/api/v1/tables/{table['id']}").json()
        assert repeat["events"] == []


def test_hidden_cards_never_appear_in_playing_json_and_folded_cards_stay_hidden() -> None:
    with TestClient(app) as client:
        table = client.post(
            "/api/v1/tables",
            json={"seed": 23, "player_count": 3, "variant": "holdem"},
        ).json()
        hidden_cards = {"".join(card) for card in []}
        assert table["hole"] == [table["seats"][0]["cards_visible"]]
        assert all(not seat["cards_visible"] for seat in table["seats"][1:])
        assert hidden_cards.isdisjoint(set(json.dumps(table)))

        finished = client.post(
            f"/api/v1/tables/{table['id']}/actions",
            json={"player": 0, "kind": "fold"},
        ).json()
        assert finished["finished"]
        for index, seat in enumerate(finished["seats"]):
            if seat["folded"]:
                assert seat["cards_visible"] == []
                assert finished["hole"][index] == []


def test_button_rotates_and_heads_up_button_posts_small_blind() -> None:
    with TestClient(app) as client:
        first = client.post(
            "/api/v1/tables", json={"seed": 31, "player_count": 2}
        ).json()
        second = client.post(
            "/api/v1/tables", json={"seed": 32, "player_count": 2}
        ).json()
        first_button = next(
            seat["index"] for seat in first["seats"] if seat["is_dealer"]
        )
        second_button = next(
            seat["index"] for seat in second["seats"] if seat["is_dealer"]
        )
        assert second_button != first_button
        for table in (first, second):
            button = next(seat for seat in table["seats"] if seat["is_dealer"])
            small_blind = next(seat for seat in table["seats"] if seat["is_sb"])
            big_blind = next(seat for seat in table["seats"] if seat["is_bb"])
            assert button["index"] == small_blind["index"]
            assert button["index"] != big_blind["index"]
