from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .cards import Card, Deck
from .evaluator import evaluate_best, evaluate_five, evaluate_omaha


class OmahaVariant(str, Enum):
    HOLDEM = "holdem"
    OMAHA = "omaha"
    OMAHA_FIVE = "omaha5"
    PINEAPPLE = "pineapple"


@dataclass(frozen=True)
class Action:
    kind: str
    amount: float = 0


@dataclass
class HandResult:
    winner: int | None
    folded: int | None
    hole: list[list[Card]]
    board: list[Card]
    stacks: list[float]
    pot: float
    log: list[str] = field(default_factory=list)
    streets_played: int = 0


@dataclass(frozen=True)
class SidePot:
    amount: float
    cap: float
    eligible: tuple[int, ...]


@dataclass
class MultiwayResult:
    winners: tuple[int, ...]
    hole: list[list[Card]]
    board: list[Card]
    stacks: list[float]
    contributions: list[float]
    side_pots: list[SidePot]
    button: int
    small_blind: int
    big_blind: int
    folded: tuple[int, ...] = ()
    log: list[str] = field(default_factory=list)


def build_side_pots(
    contributions: list[float],
    folded: set[int] | None = None,
) -> list[SidePot]:
    folded = folded or set()
    levels = sorted({value for value in contributions if value > 0})
    previous = 0.0
    pots: list[SidePot] = []
    for level in levels:
        contributors = tuple(index for index, value in enumerate(contributions) if value >= level)
        amount = (level - previous) * len(contributors)
        eligible = tuple(index for index in contributors if index not in folded)
        if amount > 0:
            pots.append(SidePot(amount, level, eligible))
        previous = level
    return pots


def play_multiway_hand(
    seed: int,
    player_count: int,
    variant: OmahaVariant = OmahaVariant.HOLDEM,
    stacks: list[float] | None = None,
    button: int = 0,
    all_in: set[int] | None = None,
    folded: set[int] | None = None,
) -> MultiwayResult:
    if not 2 <= player_count <= 9:
        raise ValueError("player_count must be between 2 and 9")
    if button not in range(player_count):
        raise ValueError("button must identify a player")
    if stacks is None:
        stacks = [100.0] * player_count
    if len(stacks) != player_count or any(value < 0 for value in stacks):
        raise ValueError("stacks must contain one non-negative value per player")
    all_in = set(all_in or ())
    folded = set(folded or ())
    if (all_in | folded) - set(range(player_count)):
        raise ValueError("player indexes are out of range")
    if variant is OmahaVariant.OMAHA:
        hole_count = 4
    elif variant is OmahaVariant.OMAHA_FIVE:
        hole_count = 5
    else:
        hole_count = 2
    deck = Deck(seed)
    hole = [deck.deal(hole_count) for _ in range(player_count)]
    board = deck.deal(5)
    remaining = list(stacks)
    contributions = [0.0] * player_count
    small_blind = (button + 1) % player_count
    big_blind = (button + 2) % player_count if player_count > 2 else button
    if player_count == 2:
        big_blind = (button + 1) % player_count
        small_blind = button
    for player, blind in ((small_blind, 0.5), (big_blind, 1.0)):
        payment = min(remaining[player], blind)
        remaining[player] -= payment
        contributions[player] += payment
    for player in range(player_count):
        if player in folded:
            continue
        if player in all_in:
            payment = remaining[player]
        else:
            payment = min(remaining[player], 1.0 - contributions[player])
        remaining[player] -= payment
        contributions[player] += payment
    side_pots = build_side_pots(contributions, folded)
    scores = {
        index: evaluate_omaha(cards, board) if variant in (OmahaVariant.OMAHA, OmahaVariant.OMAHA_FIVE)
        else evaluate_best(cards, board)
        for index, cards in enumerate(hole)
        if index not in folded
    }
    payouts = [0.0] * player_count
    winners: set[int] = set()
    for side_pot in side_pots:
        if not side_pot.eligible:
            continue
        best = max(scores[index] for index in side_pot.eligible)
        eligible_winners = [index for index in side_pot.eligible if scores[index] == best]
        winners.update(eligible_winners)
        share, remainder = divmod(round(side_pot.amount * 100), len(eligible_winners))
        for offset, winner in enumerate(eligible_winners):
            payouts[winner] += (share + (offset < remainder)) / 100
    result_stacks = [remaining[index] + payouts[index] for index in range(player_count)]
    if round(sum(result_stacks), 8) != round(sum(stacks), 8):
        raise AssertionError("chip conservation violated")
    return MultiwayResult(
        tuple(sorted(winners)), hole, board, result_stacks, contributions, side_pots,
        button, small_blind, big_blind, tuple(sorted(folded)),
    )


def play_five_card_draw(
    seed: int,
    draw_indices: list[list[int]] | None = None,
    stacks: list[float] | None = None,
) -> MultiwayResult:
    player_count = 2
    deck = Deck(seed)
    hole = [deck.deal(5) for _ in range(player_count)]
    draw_indices = draw_indices or [[], []]
    if len(draw_indices) != player_count:
        raise ValueError("draw_indices must contain one list per player")
    for player, indexes in enumerate(draw_indices):
        if len(set(indexes)) != len(indexes) or any(index not in range(5) for index in indexes):
            raise ValueError("draw indexes must be distinct values from 0 to 4")
        replacement = deck.deal(len(indexes))
        for index, card in zip(indexes, replacement):
            hole[player][index] = card
    board: list[Card] = []
    starting = stacks or [100.0, 100.0]
    if len(starting) != 2 or any(value < 0 for value in starting):
        raise ValueError("stacks must contain two non-negative values")
    remaining = starting.copy()
    contributions = [min(remaining[0], 0.5), min(remaining[1], 1.0)]
    remaining[0] -= contributions[0]
    remaining[1] -= contributions[1]
    side_pots = build_side_pots(contributions)
    payouts = [0.0, 0.0]
    scores = [evaluate_five(cards) for cards in hole]
    winners = tuple(index for index, score in enumerate(scores) if score == max(scores))
    for side_pot in side_pots:
        share, remainder = divmod(round(side_pot.amount * 100), len(winners))
        for offset, winner in enumerate(winners):
            payouts[winner] += (share + (offset < remainder)) / 100
    result_stacks = [remaining[index] + payouts[index] for index in range(2)]
    return MultiwayResult(
        winners, hole, board, result_stacks, contributions, side_pots,
        button=0, small_blind=0, big_blind=1,
    )


def play_seven_card_stud(
    seed: int,
    player_count: int = 2,
    stacks: list[float] | None = None,
) -> MultiwayResult:
    if not 2 <= player_count <= 9:
        raise ValueError("player_count must be between 2 and 9")
    starting = stacks or [100.0] * player_count
    if len(starting) != player_count or any(value < 0 for value in starting):
        raise ValueError("stacks must contain one non-negative value per player")
    deck = Deck(seed)
    hole = [deck.deal(7) for _ in range(player_count)]
    ante = [min(value, 1.0) for value in starting]
    remaining = [value - ante[index] for index, value in enumerate(starting)]
    pot = sum(ante)
    scores = [evaluate_best(cards, []) for cards in hole]
    best = max(scores)
    winners = tuple(index for index, score in enumerate(scores) if score == best)
    payouts = [0.0] * player_count
    share, remainder = divmod(round(pot * 100), len(winners))
    for offset, winner in enumerate(winners):
        payouts[winner] += (share + (offset < remainder)) / 100
    return MultiwayResult(
        winners, hole, [], [remaining[i] + payouts[i] for i in range(player_count)],
        ante, [SidePot(pot, 1.0, tuple(range(player_count)))],
        button=0, small_blind=0, big_blind=1,
    )


def pot_limit_bounds(
    player_stack: float,
    opponent_stack: float,
    player_bet: float,
    opponent_bet: float,
    pot: float,
    raise_count: int,
) -> tuple[float, float, bool]:
    del opponent_stack
    call = max(0.0, opponent_bet - player_bet)
    max_total = min(player_bet + player_stack, opponent_bet + pot + call)
    min_total = min(player_bet + player_stack, opponent_bet + max(1.0, call))
    can_raise = raise_count < 3 and player_stack > call and max_total >= min_total
    return min_total, max_total, can_raise


def play_heads_up_hand(
    seed: int,
    variant: OmahaVariant = OmahaVariant.HOLDEM,
    actions: tuple[Action, ...] = (),
    discard: Callable[[list[Card], list[Card]], int] | None = None,
) -> HandResult:
    if variant is OmahaVariant.HOLDEM:
        hole_count, omaha = 2, False
    elif variant is OmahaVariant.PINEAPPLE:
        hole_count, omaha = 3, False
    elif variant is OmahaVariant.OMAHA:
        hole_count, omaha = 4, True
    else:
        hole_count, omaha = 5, True

    deck = Deck(seed)
    hole = [deck.deal(hole_count), deck.deal(hole_count)]
    board: list[Card] = []
    stacks = [100.0, 100.0]
    street_bets = [0.5, 1.0]
    stacks[0] -= 0.5
    stacks[1] -= 1.0
    pot = 1.5
    log = ["Player 0 posts 0.5", "Player 1 posts 1.0"]
    folded: int | None = None
    action_index = 0
    streets_played = 0
    pineapple_discarded = False

    def play_street(first_player: int, bets: list[float]) -> int | None:
        nonlocal action_index, pot
        current = first_player
        acted: set[int] = set()
        raises = 0
        while True:
            facing = max(0.0, bets[1 - current] - bets[current])
            if stacks[current] <= 0:
                acted.add(current)
                if stacks[1 - current] <= 0 or facing == 0:
                    return None
                current = 1 - current
                continue

            action = (
                actions[action_index]
                if action_index < len(actions)
                else Action("call" if facing else "check")
            )
            action_index += action_index < len(actions)
            if action.kind == "fold":
                log.append(f"Player {current} folds")
                return current
            if action.kind not in {"call", "check", "bet", "raise"}:
                raise ValueError(f"unsupported action: {action.kind}")
            if action.kind == "check" and facing:
                raise ValueError("cannot check while facing a bet")

            if action.kind in {"bet", "raise"}:
                if action.amount <= bets[1 - current]:
                    raise ValueError("raise target must exceed the opposing street bet")
                if raises >= 3:
                    raise ValueError("maximum three raises per street exceeded")
                target = action.amount
                raises += 1
                acted = {current}
            else:
                target = bets[1 - current]
                acted.add(current)

            payment = min(stacks[current], max(0.0, target - bets[current]))
            stacks[current] -= payment
            bets[current] += payment
            pot += payment
            log.append(f"Player {current} {action.kind} {payment:g}")

            if stacks[current] <= 0 and bets[current] < bets[1 - current]:
                current = 1 - current
                continue
            if bets[0] == bets[1] and len(acted) == 2:
                return None
            if stacks[0] <= 0 and stacks[1] <= 0:
                return None
            current = 1 - current

    for street_number in range(4):
        if street_number == 1:
            board.extend(deck.deal(3))
            if variant is OmahaVariant.PINEAPPLE:
                for player in range(2):
                    index = discard(hole[player], board) if discard else 0
                    if index not in range(3):
                        raise ValueError("pineapple discard index must select one hole card")
                    hole[player].pop(index)
                pineapple_discarded = True
        elif street_number > 1:
            board.extend(deck.deal(1))
        bets = street_bets if street_number == 0 else [0.0, 0.0]
        street_bets = [0.0, 0.0]
        folded = play_street(0 if street_number == 0 else 1, bets)
        streets_played = street_number + 1
        if folded is not None or (stacks[0] <= 0 and stacks[1] <= 0):
            break

    if folded is None and len(board) < 5:
        if not board:
            board.extend(deck.deal(3))
        if variant is OmahaVariant.PINEAPPLE and not pineapple_discarded:
            for player in range(2):
                index = discard(hole[player], board) if discard else 0
                if index not in range(3):
                    raise ValueError("pineapple discard index must select one hole card")
                hole[player].pop(index)
        board.extend(deck.deal(5 - len(board)))

    if folded is not None:
        winner = 1 - folded
    else:
        scores = [
            evaluate_omaha(cards, board) if omaha else evaluate_best(cards, board)
            for cards in hole
        ]
        winner = None if scores[0] == scores[1] else (0 if scores[0] > scores[1] else 1)

    if winner is None:
        stacks[0] += pot / 2
        stacks[1] += pot / 2
    else:
        stacks[winner] += pot
    if round(sum(stacks), 8) != 200.0:
        raise AssertionError("chip conservation violated")
    return HandResult(winner, folded, hole, board, stacks, pot, log, streets_played)
