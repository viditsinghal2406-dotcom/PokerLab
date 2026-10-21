from __future__ import annotations

import random
from dataclasses import dataclass

RANKS = "23456789TJQKA"
SUITS = "shdc"


@dataclass(frozen=True, order=True)
class Card:
    rank: int
    suit: int

    def __post_init__(self) -> None:
        if not 0 <= self.rank < 13 or not 0 <= self.suit < 4:
            raise ValueError("card rank and suit must be in valid ranges")

    @classmethod
    def from_text(cls, value: str) -> "Card":
        if len(value) != 2 or value[0] not in RANKS or value[1].lower() not in SUITS:
            raise ValueError(f"invalid card: {value!r}")
        return cls(RANKS.index(value[0]), SUITS.index(value[1].lower()))

    def __str__(self) -> str:
        return f"{RANKS[self.rank]}{SUITS[self.suit]}"


class SeededRng:
    """Small deterministic RNG wrapper used by simulations and tests."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def shuffle(self, values: list[Card]) -> None:
        self._random.shuffle(values)

    def random(self) -> float:
        return self._random.random()


class Deck:
    def __init__(self, seed: int | None = None) -> None:
        self.cards = [Card(rank, suit) for rank in range(13) for suit in range(4)]
        if seed is not None:
            SeededRng(seed).shuffle(self.cards)

    def deal(self, count: int) -> list[Card]:
        if count < 0 or count > len(self.cards):
            raise ValueError("cannot deal that many cards")
        dealt, self.cards = self.cards[:count], self.cards[count:]
        return dealt
