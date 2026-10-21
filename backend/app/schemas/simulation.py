from typing import Literal

from pydantic import BaseModel, Field


Variant = Literal["holdem", "omaha", "omaha5"]


class MultiwayRequest(BaseModel):
    seed: int = Field(ge=0, le=2**32 - 1)
    player_count: int = Field(ge=2, le=9)
    variant: Variant = "holdem"
    stacks: list[float] | None = Field(default=None, min_length=2, max_length=9)
    button: int = Field(default=0, ge=0, le=8)
    all_in: list[int] = Field(default_factory=list)
    folded: list[int] = Field(default_factory=list)
    policy: str | None = None
    aggression: float | None = Field(default=None, ge=0, le=1)
    bluff: float | None = Field(default=None, ge=0, le=1)
    risk: float | None = Field(default=None, ge=0, le=1)
    equity_samples: int = Field(default=12, ge=1, le=10_000)


class DrawRequest(BaseModel):
    seed: int = Field(ge=0, le=2**32 - 1)
    draw_indices: list[list[int]] = Field(
        default_factory=lambda: [[], []], min_length=2, max_length=2
    )
    stacks: list[float] | None = Field(default=None, min_length=2, max_length=2)
