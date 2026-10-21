from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from random import Random

from .cards import Card
from .evaluator import evaluate_best, evaluate_omaha
from .engine import OmahaVariant


@dataclass(frozen=True)
class PolicyConfig:
    name: str
    aggression: float
    bluff: float
    risk: float
    random: bool = False

    def __post_init__(self) -> None:
        if any(not 0 <= value <= 1 for value in (self.aggression, self.bluff, self.risk)):
            raise ValueError("policy parameters must be between 0 and 1")


POLICIES = {
    "vidit": PolicyConfig("Vidit Mode", 0.85, 0.30, 0.85),
    "aggressive": PolicyConfig("Aggressive", 0.90, 0.15, 0.50),
    "balanced": PolicyConfig("Balanced", 0.50, 0.10, 0.40),
    "conservative": PolicyConfig("Conservative", 0.20, 0.02, 0.15),
    "random": PolicyConfig("Random", 0.0, 0.0, 0.0, True),
}


def _card_key(cards: tuple[Card, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((card.rank, card.suit) for card in cards))


@lru_cache(maxsize=4096)
def _equity_cached(
    variant: OmahaVariant,
    hole_key: tuple[tuple[int, int], ...],
    board_key: tuple[tuple[int, int], ...],
    seed: int,
    samples: int,
) -> float:
    hole = tuple(Card(rank, suit) for rank, suit in hole_key)
    board = tuple(Card(rank, suit) for rank, suit in board_key)
    used = set(hole + board)
    deck = [Card(rank, suit) for rank in range(13) for suit in range(4) if Card(rank, suit) not in used]
    rng = Random(seed)
    needed_board = 5 - len(board)
    wins = 0.0
    for _ in range(samples):
        draw = rng.sample(deck, needed_board + len(hole))
        runout = board + tuple(draw[:needed_board])
        opponent = tuple(draw[needed_board:])
        if variant in (OmahaVariant.OMAHA, OmahaVariant.OMAHA_FIVE):
            own_score = evaluate_omaha(hole, runout)
            opponent_score = evaluate_omaha(opponent, runout)
        else:
            own_score = evaluate_best(hole, runout)
            opponent_score = evaluate_best(opponent, runout)
        wins += 1.0 if own_score > opponent_score else 0.5 if own_score == opponent_score else 0.0
    return wins / samples


def estimate_equity(
    variant: OmahaVariant,
    hole: list[Card],
    board: list[Card],
    seed: int = 0,
    samples: int = 12,
) -> float:
    if samples < 1 or samples > 10_000:
        raise ValueError("samples must be between 1 and 10000")
    if len(board) > 5 or len(hole) not in ({OmahaVariant.OMAHA: 4, OmahaVariant.OMAHA_FIVE: 5}.get(variant, 2),):
        raise ValueError("invalid hole or board card count")
    if len(set(hole + board)) != len(hole) + len(board):
        raise ValueError("cards must be distinct")
    return _equity_cached(variant, _card_key(tuple(hole)), _card_key(tuple(board)), seed, samples)


@dataclass(frozen=True)
class DecisionContext:
    variant: OmahaVariant
    hole: tuple[Card, ...]
    board: tuple[Card, ...]
    pot: float
    to_call: float
    minimum_raise_to: float
    maximum_raise_to: float
    can_raise: bool


@dataclass(frozen=True)
class Decision:
    kind: str
    amount: float = 0.0
    equity: float | None = None
    bluff: bool = False


def decide(
    policy: PolicyConfig,
    context: DecisionContext,
    seed: int = 0,
    samples: int = 12,
) -> Decision:
    rng = Random(seed)
    if policy.random:
        if context.to_call and rng.random() < 0.25:
            return Decision("fold")
        if context.can_raise and rng.random() >= 0.8:
            return Decision("raise", context.minimum_raise_to)
        return Decision("call" if context.to_call else "check")
    equity = estimate_equity(context.variant, list(context.hole), list(context.board), seed, samples)
    pot_odds = context.to_call / max(1e-9, context.pot + context.to_call)
    bluff = equity < 0.4 and rng.random() < policy.bluff
    raise_threshold = 0.72 - 0.17 * policy.aggression
    if context.can_raise and (equity > raise_threshold or bluff):
        size = 0.35 + policy.risk * (0.3 + rng.random() * 0.7)
        amount = min(context.maximum_raise_to, max(context.minimum_raise_to, context.pot * size))
        return Decision("raise", amount, equity, bluff)
    if not context.to_call:
        return Decision("check", equity=equity, bluff=bluff)
    if equity + 0.1 * policy.risk >= pot_odds + 0.03:
        return Decision("call", equity=equity, bluff=bluff)
    return Decision("fold", equity=equity, bluff=bluff)
