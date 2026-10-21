from pydantic import BaseModel


class SidePotResponse(BaseModel):
    amount: float
    cap: float
    eligible: list[int]


class MultiwayResponse(BaseModel):
    winners: list[int]
    hole: list[list[str]]
    board: list[str]
    stacks: list[float]
    contributions: list[float]
    side_pots: list[SidePotResponse]
    button: int
    small_blind: int
    big_blind: int
    folded: list[int]
    policy: str | None = None
    decision: str | None = None
    decision_amount: float | None = None
    decision_equity: float | None = None
