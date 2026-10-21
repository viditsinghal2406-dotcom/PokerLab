from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    values: list[float] = Field(min_length=12, max_length=100_000)
    train_fraction: float = Field(default=0.8, ge=0.5, lt=1)
    models: list[str] | None = None
    window: int = Field(default=5, ge=1, le=1000)
    order: tuple[int, int, int] = (1, 0, 0)
    rolling_origin: bool = False


class ForecastMetricsResponse(BaseModel):
    mae: float
    rmse: float
    mape: float | None
    bias: float
    residual_acf1: float


class ForecastModelResponse(BaseModel):
    name: str
    parameters: dict[str, float | int | str]
    forecast: list[float]
    metrics: ForecastMetricsResponse


class ForecastResponse(BaseModel):
    train_size: int
    test_size: int
    rolling_origin: bool
    actual: list[float]
    results: list[ForecastModelResponse]
