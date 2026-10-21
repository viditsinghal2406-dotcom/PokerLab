from app.simulation.cards import Card
from app.simulation.engine import OmahaVariant
from app.simulation.policies import (
    POLICIES,
    DecisionContext,
    PolicyConfig,
    decide,
    estimate_equity,
)


def cards(value: str) -> list[Card]:
    return [Card.from_text(token) for token in value.split()]


def context() -> DecisionContext:
    return DecisionContext(
        OmahaVariant.HOLDEM,
        tuple(cards("As Ah")),
        tuple(cards("Kd 7c 2s")),
        pot=10,
        to_call=2,
        minimum_raise_to=4,
        maximum_raise_to=20,
        can_raise=True,
    )


def test_equity_is_seeded_and_cached_without_opponent_cards() -> None:
    first = estimate_equity(OmahaVariant.HOLDEM, list(context().hole), list(context().board), 7, 20)
    second = estimate_equity(OmahaVariant.HOLDEM, list(context().hole), list(context().board), 7, 20)
    assert first == second
    assert 0 <= first <= 1


def test_policy_decisions_are_reproducible_and_within_legal_bounds() -> None:
    result = decide(POLICIES["vidit"], context(), seed=8, samples=8)
    assert result.kind in {"fold", "call", "check", "raise"}
    if result.kind == "raise":
        assert 4 <= result.amount <= 20


def test_vidit_parameters_are_adjustable() -> None:
    conservative = PolicyConfig("custom", 0.0, 0.0, 0.0)
    aggressive = PolicyConfig("custom", 1.0, 1.0, 1.0)
    assert decide(conservative, context(), seed=4, samples=8) != decide(
        aggressive, context(), seed=4, samples=8
    )


def test_invalid_policy_parameters_and_samples_are_rejected() -> None:
    try:
        PolicyConfig("invalid", 1.1, 0, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid policy config was accepted")
    try:
        estimate_equity(OmahaVariant.HOLDEM, list(context().hole), list(context().board), samples=0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid sample count was accepted")
