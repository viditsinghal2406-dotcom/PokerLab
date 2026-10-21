from pydantic import BaseModel, Field

from app.schemas.simulation import Variant


class PolicyDecisionRequest(BaseModel):
    policy: str = "vidit"
    variant: Variant = "holdem"
    hole: list[str] = Field(min_length=2, max_length=5)
    board: list[str] = Field(default_factory=list, max_length=5)
    pot: float = Field(ge=0)
    to_call: float = Field(ge=0)
    minimum_raise_to: float = Field(default=0, ge=0)
    maximum_raise_to: float = Field(default=0, ge=0)
    can_raise: bool = False
    seed: int = Field(default=0, ge=0)
    samples: int = Field(default=12, ge=1, le=10000)


class PolicyDecisionResponse(BaseModel):
    kind: str
    amount: float
    equity: float | None
    bluff: bool
