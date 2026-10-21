from typing import Literal

from pydantic import BaseModel, Field


class TableRequest(BaseModel):
    seed: int = Field(ge=0, le=2**32 - 1)
    player_count: int = Field(ge=2, le=9)
    variant: Literal["holdem", "omaha", "omaha5"] = "holdem"


class TableActionRequest(BaseModel):
    player: int = Field(ge=0, le=8)
    kind: Literal["fold", "check", "call", "raise", "all-in"]
    amount: float = Field(default=0, ge=0)


class TableEvent(BaseModel):
    seq: int
    type: Literal[
        "hand_start", "blinds_posted", "deal_hole", "deal_board",
        "fold", "check", "call", "bet", "raise", "all_in",
        "street_change", "showdown", "payout",
    ]
    player: int | None = None
    amount: float = 0
    total_bet: float = 0
    cards: list[str] = Field(default_factory=list)
    street: str
    pot_after: float
    stacks_after: list[float]
    text: str


class SeatResponse(BaseModel):
    index: int
    name: str
    stack: float
    current_bet: float
    total_committed: float
    folded: bool
    all_in: bool
    is_dealer: bool
    is_sb: bool
    is_bb: bool
    last_action: str | None = None
    cards_visible: list[str] = Field(default_factory=list)


class PotBreakdownResponse(BaseModel):
    amount: float
    cap: float
    eligible: list[int]


class TableResponse(BaseModel):
    id: str
    current_player: int
    street: str
    pot: float
    finished: bool
    board: list[str]
    hole: list[list[str]]
    winners: list[int]
    stacks: list[float]
    action_log: list[str]
    legal_actions: list[str]
    minimum_raise_to: float
    maximum_raise_to: float
    to_call: float
    pot_total: float
    pot_breakdown: list[PotBreakdownResponse]
    seats: list[SeatResponse]
    events: list[TableEvent] = Field(default_factory=list)
    hand_names: dict[int, str] = Field(default_factory=dict)
    best_five: dict[int, list[str]] = Field(default_factory=dict)
    used_cards: dict[int, list[str]] = Field(default_factory=dict)
    payouts: list[float] = Field(default_factory=list)
    won_uncontested: bool = False
