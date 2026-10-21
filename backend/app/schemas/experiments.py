from typing import Literal

from pydantic import BaseModel, Field


class ExperimentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    hypothesis: str = Field(default="", max_length=2000)
    kind: Literal["A", "B", "C", "D", "E", "F"] = "E"
    variant: Literal["holdem", "omaha", "omaha5", "pineapple"] = "holdem"
    trials: int = Field(default=3, ge=1, le=20)
    hands: int = Field(default=60, ge=2, le=500)
    seed_start: int = Field(default=1000, ge=0, le=2**32 - 1)
    aggression: float = Field(default=0.85, ge=0, le=1)
    bluff: float = Field(default=0.3, ge=0, le=1)
    risk: float = Field(default=0.85, ge=0, le=1)


class ExperimentMetric(BaseModel):
    label: str
    mean_bb_per_hand: float
    ci95: float | None
    sd_bb_per_hand: float | None
    average_max_drawdown: float
    biggest_win: float
    observations: int


class ExperimentResponse(BaseModel):
    id: int
    name: str
    hypothesis: str
    kind: str
    variant: str
    trials: int
    hands: int
    seeds: list[int]
    metric: str
    results: list[ExperimentMetric]

