from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from threading import Lock
from uuid import uuid4

from app.simulation.betting import (
    BettingState,
    apply_betting_action,
    create_betting_hand,
)
from app.simulation.engine import OmahaVariant
from app.simulation.policies import DecisionContext, POLICIES, decide
from app.schemas.table import TableEvent


@dataclass
class TableState:
    id: str
    result: BettingState
    human_player: int = 0
    action_log: list[str] = field(default_factory=list)
    event_seq: int = 0
    pending_events: list[TableEvent] = field(default_factory=list)


def _street(game: BettingState) -> str:
    return "showdown" if game.finished else ("preflop", "flop", "turn", "river")[game.street]


def _visible_cards(game: BettingState, player: int | None) -> list[str]:
    if player is None:
        return []
    if player == 0 or game.finished and player not in game.folded:
        return [str(card) for card in game.hole[player]]
    return []


def _event(state: TableState, kind: str, text: str, player: int | None = None,
           amount: float = 0, cards: list[str] | None = None) -> None:
    game = state.result
    state.event_seq += 1
    state.pending_events.append(TableEvent(
        seq=state.event_seq, type=kind, player=player, amount=amount,
        total_bet=game.street_contributions[player] if player is not None else 0,
        cards=cards or [], street=_street(game), pot_after=game.pot,
        stacks_after=[round(value, 2) for value in game.stacks], text=text,
    ))


def _record_transition(state: TableState, previous_log: int) -> None:
    game = state.result
    new_logs = game.action_log[previous_log:]
    for text in new_logs:
        if text == "Hand dealt by backend":
            _event(state, "hand_start", text)
            _event(state, "deal_hole", text, player=0, cards=_visible_cards(game, 0))
            _event(state, "blinds_posted", "Blinds posted")
            continue
        if text.startswith("Street:"):
            _event(state, "street_change", text)
            if game.street > 0:
                start = 0 if game.street == 1 else 3 if game.street == 2 else 4
                end = 3 if game.street == 1 else 4 if game.street == 2 else 5
                _event(state, "deal_board", text, cards=[str(card) for card in game.board[start:end]])
            continue
        if text.startswith("Showdown:"):
            revealed = [
                str(card)
                for index, hand in enumerate(game.hole)
                if index not in game.folded
                for card in hand
            ]
            _event(state, "showdown", text, cards=revealed)
            _event(state, "payout", text)
            continue
        if text.startswith("Player "):
            player_text, action_text = text.split(": ", 1)
            player = int(player_text.split()[1])
            action = action_text.split()[0]
            event_kind = {
                "fold": "fold", "check": "check", "call": "call",
                "raise": "raise", "all-in": "all_in",
            }.get(action, "call")
            amount = 0
            if " to " in action_text:
                amount = float(action_text.rsplit(" to ", 1)[1])
            _event(state, event_kind, text, player=player, amount=amount)


tables: dict[str, TableState] = {}
lock = Lock()


def _computer_turn(state: TableState) -> None:
    game = state.result
    while not game.finished and game.current_player != state.human_player:
        player = game.current_player
        policy = POLICIES["balanced"]
        decision = decide(
            policy,
            DecisionContext(
                game.variant, tuple(game.hole[player]), tuple(game.board[:2 + game.street]),
                game.pot, max(0.0, game.current_bet - game.street_contributions[player]),
                game.minimum_raise_to, game.maximum_raise_to, "raise" in game.legal_actions,
            ),
            game.seed + len(game.action_log),
        )
        kind = decision.kind if decision.kind in game.legal_actions else (
            "call" if "call" in game.legal_actions else "check"
        )
        amount = decision.amount if kind == "raise" else 0
        previous_log = len(game.action_log)
        apply_betting_action(game, player, kind, amount)
        _record_transition(state, previous_log)


def create_table(seed: int, player_count: int, variant: str) -> TableState:
    button = getattr(create_table, "_next_button", {}).get(player_count, 0)
    create_table._next_button = getattr(create_table, "_next_button", {})
    create_table._next_button[player_count] = (button + 1) % player_count
    result = create_betting_hand(seed, player_count, OmahaVariant(variant), button=button)
    state = TableState(str(uuid4()), result)
    state.action_log = result.action_log
    _record_transition(state, 0)
    _computer_turn(state)
    with lock:
        tables[state.id] = state
    return state


def get_table(table_id: str) -> TableState | None:
    with lock:
        return tables.get(table_id)


def apply_action(table_id: str, player: int, kind: str, amount: float = 0) -> TableState:
    state = get_table(table_id)
    if state is None:
        raise KeyError(table_id)
    previous_log = len(state.result.action_log)
    apply_betting_action(state.result, player, kind, amount)
    _record_transition(state, previous_log)
    _computer_turn(state)
    return state
