from app.simulation.cards import Card
from app.simulation.engine import (
    Action,
    OmahaVariant,
    play_heads_up_hand,
    pot_limit_bounds,
)
from app.simulation.evaluator import evaluate_best, evaluate_five, evaluate_omaha


def cards(value: str) -> list[Card]:
    return [Card.from_text(token) for token in value.split()]


def test_hand_ranking_and_tie_breaks() -> None:
    assert evaluate_five(cards("As Ks Qs Js Ts")) > evaluate_five(cards("Ah Ad Ac As Kd"))
    assert evaluate_five(cards("Ah Ad Kc Kd Qs")) > evaluate_five(cards("Ah Ad Kc Qd Js"))


def test_wheel_straight_is_lower_than_six_high_straight() -> None:
    wheel = evaluate_five(cards("As 2d 3c 4h 5s"))
    six_high = evaluate_five(cards("2s 3d 4c 5h 6s"))
    assert wheel[0] == 4
    assert wheel < six_high


def test_omaha_uses_exactly_two_hole_and_three_board_cards() -> None:
    hole = cards("As Kd Qd 2d")
    board = cards("Ks Qs Js Ts 3c")
    exact_rule = evaluate_omaha(hole, board)
    unrestricted = evaluate_best(hole, board)
    assert unrestricted[0] == 8
    assert exact_rule < unrestricted


def test_pot_limit_bounds_and_raise_cap() -> None:
    minimum, maximum, can_raise = pot_limit_bounds(100, 100, 1, 1, 10, 0)
    assert minimum == 2
    assert maximum == 11
    assert can_raise
    assert pot_limit_bounds(100, 100, 1, 1, 10, 3)[2] is False


def test_seeded_hands_are_reproducible_and_conserve_chips() -> None:
    first = play_heads_up_hand(42)
    second = play_heads_up_hand(42)
    assert first.hole == second.hole
    assert first.board == second.board
    assert first.stacks == second.stacks
    assert sum(first.stacks) == 200


def test_pineapple_discards_one_card_before_showdown() -> None:
    result = play_heads_up_hand(
        7,
        OmahaVariant.PINEAPPLE,
        discard=lambda hole, board: 1,
    )
    assert all(len(hand) == 2 for hand in result.hole)
    assert len(result.board) == 5


def test_fold_awards_pot_without_showdown() -> None:
    result = play_heads_up_hand(9, actions=(Action("fold"),))
    assert result.folded == 0
    assert result.winner == 1
    assert result.winner is not None
    assert sum(result.stacks) == 200


def test_default_actions_complete_all_four_streets() -> None:
    result = play_heads_up_hand(11)
    assert result.folded is None
    assert result.streets_played == 4
    assert len(result.board) == 5
    assert sum(result.stacks) == 200


def test_raise_sequence_terminates_after_both_players_match() -> None:
    result = play_heads_up_hand(
        12,
        actions=(
            Action("raise", 2),
            Action("call"),
            Action("check"),
            Action("check"),
            Action("check"),
            Action("check"),
            Action("check"),
            Action("check"),
        ),
    )
    assert result.folded is None
    assert result.streets_played == 4


def test_all_in_call_stops_betting_and_preserves_chips() -> None:
    result = play_heads_up_hand(
        13,
        actions=(Action("raise", 100), Action("call")),
    )
    assert result.folded is None
    assert result.streets_played == 1
    assert len(result.board) == 5
    assert sum(result.stacks) == 200


def test_pineapple_discards_after_flop_is_dealt() -> None:
    seen_board_lengths: list[int] = []

    def choose_discard(hole: list[Card], board: list[Card]) -> int:
        seen_board_lengths.append(len(board))
        return 0

    result = play_heads_up_hand(14, OmahaVariant.PINEAPPLE, discard=choose_discard)
    assert seen_board_lengths == [3, 3]
    assert all(len(hand) == 2 for hand in result.hole)
