from app.simulation.cards import Card
from app.simulation.engine import (
    build_side_pots,
    play_five_card_draw,
    play_multiway_hand,
    play_seven_card_stud,
)


def test_multiway_supports_two_to_nine_players_and_positions() -> None:
    for count in range(2, 10):
        result = play_multiway_hand(100 + count, count, button=0)
        assert len(result.hole) == count
        assert len(result.board) == 5
        assert result.small_blind == (0 if count == 2 else 1)
        assert result.big_blind == (1 if count == 2 else 2)
        assert sum(result.stacks) == count * 100


def test_side_pots_have_correct_caps_and_eligibility() -> None:
    pots = build_side_pots([10, 25, 25], folded={2})
    assert [(pot.amount, pot.cap, pot.eligible) for pot in pots] == [
        (30, 10, (0, 1)),
        (30, 25, (1,)),
    ]


def test_multiway_all_in_creates_side_pot_and_conserves_chips() -> None:
    result = play_multiway_hand(
        22,
        3,
        stacks=[10, 25, 100],
        all_in={0, 1},
    )
    assert len(result.side_pots) == 3
    assert result.side_pots[0].eligible == (0, 1, 2)
    assert result.side_pots[1].eligible == (0, 1)
    assert result.side_pots[2].eligible == (1,)
    assert sum(result.stacks) == 135


def test_multiway_folded_player_is_not_eligible_for_payout() -> None:
    result = play_multiway_hand(23, 4, folded={2})
    assert 2 not in result.winners
    assert 2 not in {winner for pot in result.side_pots for winner in pot.eligible}


def test_five_card_draw_replaces_requested_cards() -> None:
    result = play_five_card_draw(31, draw_indices=[[0, 1], []])
    assert len(result.hole) == 2
    assert len(result.hole[0]) == 5
    assert len(result.hole[1]) == 5
    assert result.hole[0][0] != result.hole[1][0]
    assert sum(result.stacks) == 200


def test_seven_card_stud_deals_seven_cards_and_conserves_chips() -> None:
    result = play_seven_card_stud(32, player_count=4)
    assert all(len(hand) == 7 for hand in result.hole)
    assert result.board == []
    assert sum(result.stacks) == 400
