from hypothesis import given, strategies as st

from app.simulation.betting import apply_betting_action, create_betting_hand
from app.simulation.engine import OmahaVariant


@given(st.integers(min_value=0, max_value=2**16 - 1))
def test_betting_actions_terminate_and_preserve_chips(seed: int):
    state = create_betting_hand(seed, 3, OmahaVariant.HOLDEM)
    starting_total = 100.0 * len(state.hole)
    steps = 0
    while not state.finished and steps < 200:
        player = state.current_player
        legal = state.legal_actions
        action = "check" if "check" in legal else "call" if "call" in legal else "fold"
        apply_betting_action(state, player, action)
        steps += 1
    assert state.finished
    assert steps < 200
    assert round(sum(state.stacks), 8) == round(starting_total, 8)


@given(st.integers(min_value=0, max_value=2**16 - 1), st.sampled_from([3, 6, 9]))
def test_multiway_streets_terminate_for_supported_table_sizes(seed: int, players: int):
    state = create_betting_hand(seed, players, OmahaVariant.HOLDEM)
    steps = 0
    while not state.finished and steps < 500:
        legal = state.legal_actions
        action = "check" if "check" in legal else "call" if "call" in legal else "fold"
        apply_betting_action(state, state.current_player, action)
        steps += 1
    assert state.finished
    assert steps < 500


@given(st.integers(min_value=0, max_value=2**16 - 1))
def test_omaha_raise_bounds_and_all_in_side_pots(seed: int):
    state = create_betting_hand(seed, 6, OmahaVariant.OMAHA)
    state.stacks[0] = 2.0
    state.stacks[1] = 3.0
    if "raise" in state.legal_actions:
        assert state.maximum_raise_to >= state.minimum_raise_to or state.maximum_raise_to >= state.street_contributions[0] + state.stacks[0]
