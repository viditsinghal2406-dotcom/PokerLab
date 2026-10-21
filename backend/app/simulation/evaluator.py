from __future__ import annotations

from itertools import combinations
from typing import Iterable

from .cards import Card

Category = int
Score = tuple[int, ...]


def evaluate_five(cards: Iterable[Card]) -> Score:
    cards = tuple(cards)
    if len(cards) != 5 or len(set(cards)) != 5:
        raise ValueError("exactly five distinct cards are required")
    ranks = sorted((card.rank for card in cards), reverse=True)
    counts: dict[int, int] = {}
    for rank in ranks:
        counts[rank] = counts.get(rank, 0) + 1
    groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
    flush = len({card.suit for card in cards}) == 1
    unique = set(ranks)
    straight_high = 0
    if len(unique) == 5:
        if max(unique) - min(unique) == 4:
            straight_high = max(unique)
        elif unique == {12, 3, 2, 1, 0}:
            straight_high = 3
    if flush and straight_high:
        return (8, straight_high)
    if groups[0][0] == 4:
        quad = groups[0][1]
        return (7, quad, groups[1][1])
    if groups[0][0] == 3 and groups[1][0] == 2:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5, *ranks)
    if straight_high:
        return (4, straight_high)
    if groups[0][0] == 3:
        return (3, groups[0][1], *sorted((r for r in ranks if r != groups[0][1]), reverse=True))
    if groups[0][0] == 2 and groups[1][0] == 2:
        pairs = sorted((groups[0][1], groups[1][1]), reverse=True)
        kicker = next(r for r in ranks if r not in pairs)
        return (2, *pairs, kicker)
    if groups[0][0] == 2:
        pair = groups[0][1]
        return (1, pair, *sorted((r for r in ranks if r != pair), reverse=True))
    return (0, *ranks)


def evaluate_best(hole: Iterable[Card], board: Iterable[Card]) -> Score:
    cards = tuple(hole) + tuple(board)
    if len(cards) < 5:
        raise ValueError("at least five cards are required")
    return max(evaluate_five(combo) for combo in combinations(cards, 5))


def evaluate_omaha(hole: Iterable[Card], board: Iterable[Card]) -> Score:
    hole, board = tuple(hole), tuple(board)
    if len(hole) not in (4, 5) or len(board) != 5:
        raise ValueError("Omaha requires four or five hole cards and five board cards")
    return max(
        evaluate_five(hole_combo + board_combo)
        for hole_combo in combinations(hole, 2)
        for board_combo in combinations(board, 3)
    )
