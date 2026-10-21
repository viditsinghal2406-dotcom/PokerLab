from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from math import floor

from .cards import Card, Deck
from .engine import OmahaVariant, SidePot, build_side_pots
from .evaluator import evaluate_best, evaluate_five, evaluate_omaha


STREETS = ("preflop", "flop", "turn", "river")


@dataclass
class BettingState:
    seed: int
    variant: OmahaVariant
    button: int
    hole: list[list[Card]]
    board: list[Card]
    stacks: list[float]
    contributions: list[float]
    street_contributions: list[float]
    folded: set[int] = field(default_factory=set)
    acted: set[int] = field(default_factory=set)
    street: int = 0
    current_player: int = 0
    current_bet: float = 0.0
    minimum_raise: float = 1.0
    raises: int = 0
    finished: bool = False
    winners: tuple[int, ...] = ()
    action_log: list[str] = field(default_factory=list)
    last_actions: list[str | None] = field(default_factory=list)
    payouts: list[float] = field(default_factory=list)
    hand_names: dict[int, str] = field(default_factory=dict)
    best_five: dict[int, list[Card]] = field(default_factory=dict)
    used_cards: dict[int, list[Card]] = field(default_factory=dict)
    won_uncontested: bool = False

    @property
    def pot(self) -> float:
        return round(sum(self.contributions), 2)

    @property
    def all_in(self) -> set[int]:
        return {i for i, stack in enumerate(self.stacks) if stack <= 1e-9}

    @property
    def legal_actions(self) -> list[str]:
        if self.finished:
            return []
        if self.current_player in self.folded or self.current_player in self.all_in:
            return []
        actions = ["fold"]
        to_call = self.current_bet - self.street_contributions[self.current_player]
        actions.append("check" if to_call <= 1e-9 else "call")
        if self.raises < 3 and self.stacks[self.current_player] > to_call + 1e-9:
            actions.append("raise")
        if self.stacks[self.current_player] > 1e-9:
            actions.append("all-in")
        return actions

    @property
    def minimum_raise_to(self) -> float:
        return self.current_bet + self.minimum_raise

    @property
    def maximum_raise_to(self) -> float:
        player = self.current_player
        to_call = max(0.0, self.current_bet - self.street_contributions[player])
        if self.variant in (OmahaVariant.OMAHA, OmahaVariant.OMAHA_FIVE):
            pot_after_call = self.pot + to_call
            return min(
                self.street_contributions[player] + self.stacks[player],
                self.current_bet + pot_after_call,
            )
        return self.street_contributions[player] + self.stacks[player]


def create_betting_hand(
    seed: int, player_count: int, variant: OmahaVariant, button: int = 0,
) -> BettingState:
    if not 2 <= player_count <= 9:
        raise ValueError("player_count must be between 2 and 9")
    if button not in range(player_count):
        raise ValueError("button must identify a player")
    hole_count = 4 if variant is OmahaVariant.OMAHA else 5 if variant is OmahaVariant.OMAHA_FIVE else 2
    deck = Deck(seed)
    hole = [deck.deal(hole_count) for _ in range(player_count)]
    board = deck.deal(5)
    stacks = [100.0] * player_count
    street_contributions = [0.0] * player_count
    small_blind = button if player_count == 2 else (button + 1) % player_count
    big_blind = (button + 1) % player_count if player_count == 2 else (button + 2) % player_count
    contributions = [0.0] * player_count
    for player, blind in ((small_blind, 0.5), (big_blind, 1.0)):
        stacks[player] -= blind
        contributions[player] = blind
        street_contributions[player] = blind
    first = small_blind if player_count == 2 else (big_blind + 1) % player_count
    state = BettingState(
        seed, variant, button, hole, board, stacks, contributions,
        street_contributions, current_player=first, current_bet=1.0,
        last_actions=[None] * player_count, payouts=[0.0] * player_count,
    )
    state.action_log.append("Hand dealt by backend")
    return state


def _next_player(state: BettingState, start: int | None = None) -> int:
    count = len(state.hole)
    player = state.current_player if start is None else start
    for offset in range(1, count + 1):
        candidate = (player + offset) % count
        if candidate not in state.folded and candidate not in state.all_in:
            return candidate
    return player


def _complete_street(state: BettingState) -> bool:
    eligible = {
        i for i in range(len(state.hole))
        if i not in state.folded and i not in state.all_in
    }
    if len(eligible) <= 1 or (eligible and eligible <= state.acted and all(
        state.street_contributions[i] == state.current_bet for i in eligible
    )):
        if state.street == 3 or len(state.folded) >= len(state.hole) - 1:
            finish_betting_hand(state)
            return True
        state.street += 1
        state.street_contributions = [0.0] * len(state.hole)
        state.current_bet = 0.0
        state.minimum_raise = 1.0
        state.raises = 0
        state.acted.clear()
        state.current_player = _next_player(state, state.button)
        state.action_log.append(f"Street: {STREETS[state.street]}")
        if len(eligible) == 0:
            finish_betting_hand(state)
        return True
    return False


def apply_betting_action(state: BettingState, player: int, kind: str, amount: float = 0) -> BettingState:
    if state.finished:
        raise ValueError("hand is already finished")
    if player != state.current_player:
        raise ValueError("action is not for the current player")
    if kind not in state.legal_actions:
        raise ValueError("action is not legal")
    to_call = max(0.0, state.current_bet - state.street_contributions[player])
    if kind == "fold":
        state.folded.add(player)
    elif kind == "check" and to_call > 1e-9:
        raise ValueError("cannot check facing a bet")
    elif kind == "call":
        payment = min(to_call, state.stacks[player])
        state.stacks[player] = _money(state.stacks[player] - payment)
        state.contributions[player] = _money(state.contributions[player] + payment)
        state.street_contributions[player] = _money(state.street_contributions[player] + payment)
    elif kind == "all-in":
        amount = state.street_contributions[player] + state.stacks[player]
        if amount > state.current_bet:
            state.minimum_raise = max(state.minimum_raise, amount - state.current_bet)
            state.current_bet = amount
            state.raises += 1
            state.acted.clear()
        state.contributions[player] = _money(state.contributions[player] + state.stacks[player])
        state.street_contributions[player] = _money(amount)
        state.stacks[player] = 0.0
    elif kind == "raise":
        all_in_raise = amount >= state.street_contributions[player] + state.stacks[player] - 1e-9
        if (amount < state.minimum_raise_to - 1e-9 and not all_in_raise) or amount > state.maximum_raise_to + 1e-9:
            raise ValueError("raise is outside the legal bounds")
        amount = _half_bb(amount)
        increase = amount - state.street_contributions[player]
        state.stacks[player] = _money(state.stacks[player] - increase)
        state.contributions[player] = _money(state.contributions[player] + increase)
        state.street_contributions[player] = _money(amount)
        state.minimum_raise = max(state.minimum_raise, amount - state.current_bet)
        state.current_bet = amount
        state.raises += 1
        state.acted.clear()
    state.acted.add(player)
    state.last_actions[player] = kind
    state.action_log.append(f"Player {player}: {kind}" + (f" to {amount:g}" if kind == "raise" else ""))
    if not _complete_street(state):
        state.current_player = _next_player(state)
    return state


def finish_betting_hand(state: BettingState) -> None:
    if state.finished:
        return
    eligible = [i for i in range(len(state.hole)) if i not in state.folded]
    state.won_uncontested = len(eligible) == 1
    if len(eligible) == 1:
        winners = tuple(eligible)
    else:
        scores = {
            i: evaluate_omaha(state.hole[i], state.board)
            if state.variant in (OmahaVariant.OMAHA, OmahaVariant.OMAHA_FIVE)
            else evaluate_best(state.hole[i], state.board)
            for i in eligible
        }
        best = max(scores.values())
        winners = tuple(i for i in eligible if scores[i] == best)
    payouts = [0.0] * len(state.hole)
    for pot in build_side_pots(state.contributions, state.folded):
        eligible_pot = [i for i in pot.eligible if i in winners or len(winners) > 1]
        if not eligible_pot:
            continue
        if len(winners) > 1:
            eligible_pot = [i for i in pot.eligible if i in winners]
        share, remainder = divmod(round(pot.amount * 100), len(eligible_pot))
        for offset, winner in enumerate(eligible_pot):
            payouts[winner] += (share + (offset < remainder)) / 100
    for index, payout in enumerate(payouts):
        state.stacks[index] = _money(state.stacks[index] + payout)
    if round(sum(state.stacks), 2) != round(100.0 * len(state.hole), 2):
        raise AssertionError("chip conservation violated")
    state.winners = winners
    state.payouts = [_money(value) for value in payouts]
    for player in winners:
        if state.variant in (OmahaVariant.OMAHA, OmahaVariant.OMAHA_FIVE):
            combos = (
                tuple(hole_cards) + tuple(board_cards)
                for hole_cards in combinations(state.hole[player], 2)
                for board_cards in combinations(state.board, 3)
            )
        else:
            combos = combinations(tuple(state.hole[player]) + tuple(state.board), 5)
        best_combo = max(combos, key=evaluate_five)
        score = evaluate_five(best_combo)
        state.best_five[player] = list(best_combo)
        state.used_cards[player] = list(best_combo)
        state.hand_names[player] = _hand_name(score)
    state.finished = True
    state.action_log.append(f"Showdown: winner(s) {', '.join(map(str, winners))}")


def _half_bb(value: float) -> float:
    return round(floor(value * 2 + 1e-9) / 2, 2)


def _money(value: float) -> float:
    return round(value + 1e-9, 2)


def _hand_name(score: tuple[int, ...]) -> str:
    return (
        "High card", "Pair", "Two pair", "Three of a kind", "Straight",
        "Flush", "Full house", "Four of a kind", "Straight flush",
    )[score[0]]
