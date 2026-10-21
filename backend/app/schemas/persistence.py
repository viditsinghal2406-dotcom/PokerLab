from pydantic import BaseModel, Field

from app.schemas.simulation import Variant


class StrategyConfigRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    policy: str
    parameters: dict[str, float] = Field(default_factory=dict)


class StrategyConfigResponse(StrategyConfigRequest):
    id: int


class JobRequest(BaseModel):
    seed: int = Field(ge=0, le=2**32 - 1)
    variant: Variant = "holdem"
    player_count: int = Field(ge=2, le=9)
    hands: int = Field(ge=1, le=10_000)


class JobResponse(BaseModel):
    id: int
    status: str
    hands_requested: int
    hands_completed: int
    error: str | None = None


class JobResultResponse(JobResponse):
    results: list[dict]
