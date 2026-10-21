from pydantic import BaseModel, Field


class AtsaRequest(BaseModel):
    values: list[float] = Field(min_length=8, max_length=100_000)
    order: tuple[int, int, int] = (1, 0, 0)
    horizon: int = Field(default=5, ge=1, le=1000)
    lags: int = Field(default=10, ge=1, le=100)


class DiagnosticResponse(BaseModel):
    statistic: float
    p_value: float
    lags: int
    conclusion: str


class AtsaResponse(BaseModel):
    adf: DiagnosticResponse
    kpss: DiagnosticResponse
    acf: list[float]
    pacf: list[float]
    arima_order: tuple[int, int, int]
    aic: float
    bic: float
    forecast: list[float]
    lower: list[float]
    upper: list[float]
    residuals: list[float]
    ljung_box_p_value: float
