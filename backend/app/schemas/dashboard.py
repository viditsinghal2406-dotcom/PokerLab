from pydantic import BaseModel


class DashboardResponse(BaseModel):
    experiments_count: int
    completed_jobs_count: int
    strategy_configs_count: int
    recent_experiments: list[dict]
    best_recent_condition: str | None = None
    best_recent_mean_bb_per_hand: float | None = None
