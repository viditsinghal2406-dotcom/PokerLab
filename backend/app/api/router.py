from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.schemas.health import HealthResponse
from app.schemas.simulation import DrawRequest, MultiwayRequest
from app.schemas.simulation_result import MultiwayResponse, SidePotResponse
from app.schemas.policy import PolicyDecisionRequest, PolicyDecisionResponse
from app.simulation.cards import Card
from app.simulation.engine import (
    OmahaVariant,
    build_side_pots,
    play_five_card_draw,
    play_multiway_hand,
    play_seven_card_stud,
)
from app.simulation.policies import POLICIES, DecisionContext, PolicyConfig, decide
from app.db.models import AnalyticsRun, SimulationRun, StrategyConfig
from app.db.session import get_session
from app.jobs import cancel_run, start_run
from app.table import apply_action, create_table, get_table
from app.schemas.persistence import (
    JobRequest,
    JobResponse,
    JobResultResponse,
    StrategyConfigRequest,
    StrategyConfigResponse,
)
from app.schemas.table import (
    TableActionRequest, TableRequest, TableResponse, PotBreakdownResponse,
    SeatResponse,
)
from app.schemas.atsa import AtsaRequest, AtsaResponse, DiagnosticResponse
from app.analytics.atsa import arima, correlations, stationarity
from app.analytics.forecasting import evaluate_forecasts
from app.schemas.forecasting import (
    ForecastMetricsResponse,
    ForecastModelResponse,
    ForecastRequest,
    ForecastResponse,
)
from app.schemas.experiments import ExperimentRequest, ExperimentResponse, ExperimentMetric
from app.schemas.dashboard import DashboardResponse
from app.schemas.history import HistoryItem, HistoryResponse
from app.db.models import Experiment, StrategyConfig
from app.experiments import run_experiment
from app.reports.experiment import csv_bytes, html_report, parquet_bytes, pdf_bytes
import json

api_router = APIRouter()


@api_router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="pokerlab-api", version="0.1.0")


def _experiment_response(row: Experiment) -> ExperimentResponse:
    data = json.loads(row.metadata_json)
    return ExperimentResponse(id=row.id, name=row.name, hypothesis=row.hypothesis,
                              kind=data["kind"], variant=data["variant"],
                              trials=data["trials"], hands=data["hands"],
                              seeds=data["seeds"], metric=data["metric"],
                              results=[ExperimentMetric(**item) for item in data["results"]])


@api_router.post("/experiments/run", response_model=ExperimentResponse, tags=["experiments"])
def create_experiment(request: ExperimentRequest, session: Session = Depends(get_session)) -> ExperimentResponse:
    try:
        seeds, metrics = run_experiment(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    record = {
        "kind": request.kind, "variant": request.variant, "trials": request.trials,
        "hands": request.hands, "seeds": seeds, "metric": "profit per hand in BB",
        "results": [metric.__dict__ for metric in metrics],
    }
    row = Experiment(name=request.name, hypothesis=request.hypothesis, metadata_json=json.dumps(record))
    session.add(row)
    session.commit()
    session.refresh(row)
    return _experiment_response(row)


@api_router.get("/experiments/{experiment_id}", response_model=ExperimentResponse, tags=["experiments"])
def get_experiment(experiment_id: int, session: Session = Depends(get_session)) -> ExperimentResponse:
    row = session.get(Experiment, experiment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    return _experiment_response(row)


@api_router.get("/experiments", tags=["experiments"])
def list_experiments(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.query(Experiment).order_by(Experiment.created_at.desc()).all()
    return [{"id": row.id, "name": row.name, "hypothesis": row.hypothesis,
             "created_at": row.created_at.isoformat()} for row in rows]


@api_router.delete("/experiments/{experiment_id}", status_code=204, tags=["experiments"])
def delete_experiment(experiment_id: int, session: Session = Depends(get_session)) -> None:
    row = session.get(Experiment, experiment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    session.delete(row)
    session.commit()


@api_router.get("/dashboard", response_model=DashboardResponse, tags=["dashboard"])
def dashboard(session: Session = Depends(get_session)) -> DashboardResponse:
    experiments = session.query(Experiment).order_by(Experiment.created_at.desc()).all()
    completed_jobs = session.query(SimulationRun).filter(SimulationRun.status == "completed").count()
    configs = session.query(StrategyConfig).count()
    recent = [{"id": row.id, "name": row.name, "created_at": row.created_at.isoformat()}
              for row in experiments[:5]]
    recent_metrics = [
        metric
        for row in experiments[:5]
        for metric in json.loads(row.metadata_json).get("results", [])
    ]
    best = max(recent_metrics, key=lambda item: item["mean_bb_per_hand"], default=None)
    return DashboardResponse(
        experiments_count=len(experiments),
        completed_jobs_count=completed_jobs,
        strategy_configs_count=configs,
        recent_experiments=recent,
        best_recent_condition=best["label"] if best else None,
        best_recent_mean_bb_per_hand=best["mean_bb_per_hand"] if best else None,
    )


@api_router.get("/experiments/{experiment_id}/export.csv", tags=["experiments"])
def export_experiment(experiment_id: int, session: Session = Depends(get_session)) -> PlainTextResponse:
    row = session.get(Experiment, experiment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    data = _experiment_response(row)
    return Response(csv_bytes(data), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="experiment-{data.id}.csv"'})


def _get_experiment_or_404(experiment_id: int, session: Session) -> ExperimentResponse:
    row = session.get(Experiment, experiment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="experiment not found")
    return _experiment_response(row)


@api_router.get("/experiments/{experiment_id}/report.html", tags=["experiments"])
def report_experiment(experiment_id: int, session: Session = Depends(get_session)) -> Response:
    data = _get_experiment_or_404(experiment_id, session)
    return Response(html_report(data), media_type="text/html",
                    headers={"Content-Disposition": f'attachment; filename="experiment-{data.id}.html"'})


@api_router.get("/experiments/{experiment_id}/export.parquet", tags=["experiments"])
def export_experiment_parquet(experiment_id: int, session: Session = Depends(get_session)) -> Response:
    data = _get_experiment_or_404(experiment_id, session)
    return Response(parquet_bytes(data), media_type="application/vnd.apache.parquet",
                    headers={"Content-Disposition": f'attachment; filename="experiment-{data.id}.parquet"'})


@api_router.get("/experiments/{experiment_id}/report.pdf", tags=["experiments"])
def pdf_experiment(experiment_id: int, session: Session = Depends(get_session)) -> Response:
    data = _get_experiment_or_404(experiment_id, session)
    return Response(pdf_bytes(data), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="experiment-{data.id}.pdf"'})


@api_router.post("/analytics/atsa", response_model=AtsaResponse, tags=["analytics"])
def run_atsa(request: AtsaRequest, session: Session = Depends(get_session)) -> AtsaResponse:
    diagnostics = stationarity(request.values)
    model = arima(request.values, request.order, request.horizon)
    correlation = correlations(request.values, request.lags)
    response = AtsaResponse(
        adf=DiagnosticResponse(**diagnostics["adf"].__dict__),
        kpss=DiagnosticResponse(**diagnostics["kpss"].__dict__),
        acf=correlation["acf"],
        pacf=correlation["pacf"],
        arima_order=model.order,
        aic=model.aic,
        bic=model.bic,
        forecast=model.forecast,
        lower=model.lower,
        upper=model.upper,
        residuals=model.residuals,
        ljung_box_p_value=model.ljung_box_p_value,
    )
    session.add(AnalyticsRun(
        kind="atsa", name="ATSA analysis",
        request_json=request.model_dump_json(), result_json=response.model_dump_json(),
    ))
    session.commit()
    return response


@api_router.post("/analytics/forecast", response_model=ForecastResponse, tags=["analytics"])
def run_forecast(request: ForecastRequest, session: Session = Depends(get_session)) -> ForecastResponse:
    try:
        results = evaluate_forecasts(
            request.values,
            request.train_fraction,
            request.models,
            request.window,
            request.order,
            request.rolling_origin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    cut = int(len(request.values) * request.train_fraction)
    response = ForecastResponse(
        train_size=cut,
        test_size=len(request.values) - cut,
        rolling_origin=request.rolling_origin,
        actual=request.values[cut:],
        results=[
            ForecastModelResponse(
                name=result.name,
                parameters=result.parameters,
                forecast=result.forecast,
                metrics=ForecastMetricsResponse(**result.metrics.__dict__),
            )
            for result in results
        ],
    )
    session.add(AnalyticsRun(
        kind="forecast", name="Forecast evaluation",
        request_json=request.model_dump_json(), result_json=response.model_dump_json(),
    ))
    session.commit()
    return response


@api_router.get("/analytics/history", response_model=HistoryResponse, tags=["analytics"])
def analytics_history(session: Session = Depends(get_session)) -> HistoryResponse:
    rows = session.query(AnalyticsRun).order_by(AnalyticsRun.created_at.desc()).all()
    return HistoryResponse(items=[
        HistoryItem(id=row.id, kind=row.kind, name=row.name, created_at=row.created_at.isoformat())
        for row in rows
    ])


@api_router.get("/analytics/series", tags=["analytics"])
def available_series(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.query(AnalyticsRun).order_by(AnalyticsRun.created_at.desc()).all()
    return [{"id": row.id, "kind": row.kind, "name": row.name,
             "created_at": row.created_at.isoformat()} for row in rows]


@api_router.get("/analytics/history/{run_id}", tags=["analytics"])
def get_analytics_history(run_id: int, session: Session = Depends(get_session)) -> dict:
    row = session.get(AnalyticsRun, run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="analytics run not found")
    return {"id": row.id, "kind": row.kind, "name": row.name,
            "request": json.loads(row.request_json), "result": json.loads(row.result_json)}


@api_router.delete("/analytics/history/{run_id}", status_code=204, tags=["analytics"])
def delete_analytics_history(run_id: int, session: Session = Depends(get_session)) -> None:
    row = session.get(AnalyticsRun, run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="analytics run not found")
    session.delete(row)
    session.commit()


def _table_response(state) -> TableResponse:
    game = state.result
    visible_hole = (
        [
            [] if index in game.folded else [str(card) for card in hand]
            for index, hand in enumerate(game.hole)
        ]
        if game.finished
        else [[str(card) for card in game.hole[state.human_player]]]
    )
    seat_rows = []
    for index, stack in enumerate(game.stacks):
        seat_rows.append(SeatResponse(
            index=index, name="You" if index == 0 else f"Player {index + 1}",
            stack=round(stack, 2),
            current_bet=round(game.street_contributions[index], 2),
            total_committed=round(game.contributions[index], 2),
            folded=index in game.folded, all_in=index in game.all_in,
            is_dealer=index == game.button,
            is_sb=index == (game.button if len(game.hole) == 2 else (game.button + 1) % len(game.hole)),
            is_bb=index == ((game.button + 1) % len(game.hole) if len(game.hole) == 2 else (game.button + 2) % len(game.hole)),
            last_action=game.last_actions[index] if game.last_actions else None,
            cards_visible=visible_hole[index] if game.finished and index < len(visible_hole) else (
                visible_hole[0] if index == 0 else []
            ),
        ))
    response = TableResponse(
        id=state.id,
        current_player=game.current_player,
        street=("showdown" if game.finished else ("preflop", "flop", "turn", "river")[game.street]),
        pot=game.pot,
        finished=game.finished,
        board=[str(card) for card in game.board[:0 if game.street == 0 else 3 if game.street == 1 else 4 if game.street == 2 else 5]],
        # Hidden cards remain private during play; reveal all hands only at showdown.
        hole=visible_hole,
        winners=list(game.winners),
        stacks=[round(value, 2) for value in game.stacks],
        action_log=game.action_log,
        legal_actions=game.legal_actions,
        minimum_raise_to=game.minimum_raise_to,
        maximum_raise_to=game.maximum_raise_to,
        to_call=round(max(0.0, game.current_bet - game.street_contributions[game.current_player]), 2),
        pot_total=game.pot,
        pot_breakdown=[
            PotBreakdownResponse(amount=round(pot.amount, 2), cap=round(pot.cap, 2), eligible=list(pot.eligible))
            for pot in build_side_pots(game.contributions, game.folded)
        ],
        seats=seat_rows,
        events=state.pending_events.copy(),
        hand_names=game.hand_names,
        best_five={index: [str(card) for card in cards] for index, cards in game.best_five.items()},
        used_cards={index: [str(card) for card in cards] for index, cards in game.used_cards.items()},
        payouts=[round(value, 2) for value in game.payouts],
        won_uncontested=game.won_uncontested,
    )
    state.pending_events.clear()
    return response


@api_router.post("/tables", response_model=TableResponse, tags=["table"])
def create_playable_table(request: TableRequest) -> TableResponse:
    return _table_response(create_table(request.seed, request.player_count, request.variant))


@api_router.get("/tables/{table_id}", response_model=TableResponse, tags=["table"])
def get_playable_table(table_id: str) -> TableResponse:
    state = get_table(table_id)
    if state is None:
        raise HTTPException(status_code=404, detail="table not found")
    return _table_response(state)


@api_router.post("/tables/{table_id}/actions", response_model=TableResponse, tags=["table"])
def submit_table_action(table_id: str, request: TableActionRequest) -> TableResponse:
    try:
        return _table_response(apply_action(table_id, request.player, request.kind, request.amount))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="table not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _response(result, **policy_fields) -> MultiwayResponse:
    return MultiwayResponse(
        winners=list(result.winners),
        hole=[[str(card) for card in hand] for hand in result.hole],
        board=[str(card) for card in result.board],
        stacks=result.stacks,
        contributions=result.contributions,
        side_pots=[
            SidePotResponse(amount=pot.amount, cap=pot.cap, eligible=list(pot.eligible))
            for pot in result.side_pots
        ],
        button=result.button,
        small_blind=result.small_blind,
        big_blind=result.big_blind,
        folded=list(result.folded),
        **policy_fields,
    )


@api_router.post("/simulations/multiway", response_model=MultiwayResponse, tags=["simulation"])
def multiway(request: MultiwayRequest) -> MultiwayResponse:
    result = play_multiway_hand(
        seed=request.seed,
        player_count=request.player_count,
        variant=OmahaVariant(request.variant),
        stacks=request.stacks,
        button=request.button,
        all_in=set(request.all_in),
        folded=set(request.folded),
    )
    policy_fields: dict[str, object] = {}
    if request.policy is not None:
        policy = POLICIES.get(request.policy)
        if policy is None:
            raise HTTPException(status_code=400, detail=f"unknown policy: {request.policy}")
        custom = PolicyConfig(
            policy.name,
            request.aggression if request.aggression is not None else policy.aggression,
            request.bluff if request.bluff is not None else policy.bluff,
            request.risk if request.risk is not None else policy.risk,
            policy.random,
        )
        acting_hole = result.hole[0]
        decision = decide(
            custom,
            DecisionContext(
                OmahaVariant(request.variant),
                tuple(acting_hole),
                tuple(result.board),
                sum(result.contributions),
                0,
                1,
                100,
                True,
            ),
            request.seed,
            request.equity_samples,
        )
        policy_fields = {
            "policy": request.policy,
            "decision": decision.kind,
            "decision_amount": decision.amount,
            "decision_equity": decision.equity,
        }
    return _response(result, **policy_fields)


@api_router.post("/simulations/draw", response_model=MultiwayResponse, tags=["simulation"])
def draw(request: DrawRequest) -> MultiwayResponse:
    return _response(play_five_card_draw(request.seed, request.draw_indices, request.stacks))


@api_router.post("/simulations/stud", response_model=MultiwayResponse, tags=["simulation"])
def stud(request: MultiwayRequest) -> MultiwayResponse:
    result = play_seven_card_stud(
        seed=request.seed,
        player_count=request.player_count,
        stacks=request.stacks,
    )
    return _response(result)


@api_router.post(
    "/policies/decision",
    response_model=PolicyDecisionResponse,
    tags=["policies"],
)
def policy_decision(request: PolicyDecisionRequest) -> PolicyDecisionResponse:
    policy = POLICIES.get(request.policy)
    if policy is None:
        raise HTTPException(status_code=400, detail=f"unknown policy: {request.policy}")
    variant = OmahaVariant(request.variant)
    hole = tuple(Card.from_text(value) for value in request.hole)
    board = tuple(Card.from_text(value) for value in request.board)
    result = decide(
        policy,
        DecisionContext(
            variant, hole, board, request.pot, request.to_call,
            request.minimum_raise_to, request.maximum_raise_to, request.can_raise,
        ),
        request.seed,
        request.samples,
    )
    return PolicyDecisionResponse(
        kind=result.kind, amount=result.amount, equity=result.equity, bluff=result.bluff
    )


@api_router.post("/strategy-configs", response_model=StrategyConfigResponse, tags=["persistence"])
def create_strategy_config(
    request: StrategyConfigRequest, session: Session = Depends(get_session)
) -> StrategyConfigResponse:
    if request.policy not in POLICIES:
        raise HTTPException(status_code=400, detail=f"unknown policy: {request.policy}")
    row = StrategyConfig(
        name=request.name, policy=request.policy, parameters_json=json.dumps(request.parameters)
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return StrategyConfigResponse(id=row.id, name=row.name, policy=row.policy, parameters=request.parameters)


@api_router.get("/strategy-configs", response_model=list[StrategyConfigResponse], tags=["persistence"])
def list_strategy_configs(session: Session = Depends(get_session)) -> list[StrategyConfigResponse]:
    return [
        StrategyConfigResponse(id=row.id, name=row.name, policy=row.policy,
                               parameters=json.loads(row.parameters_json))
        for row in session.query(StrategyConfig).order_by(StrategyConfig.created_at.desc()).all()
    ]


@api_router.delete("/strategy-configs/{config_id}", status_code=204, tags=["persistence"])
def delete_strategy_config(config_id: int, session: Session = Depends(get_session)) -> None:
    row = session.get(StrategyConfig, config_id)
    if row is None:
        raise HTTPException(status_code=404, detail="strategy config not found")
    session.delete(row)
    session.commit()


@api_router.post("/jobs/simulations", response_model=JobResponse, status_code=202, tags=["jobs"])
def create_simulation_job(request: JobRequest) -> JobResponse:
    try:
        job_id = start_run(request.seed, request.variant, request.player_count, request.hands)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return JobResponse(id=job_id, status="queued", hands_requested=request.hands, hands_completed=0)


def _job_response(row: SimulationRun) -> JobResponse:
    return JobResponse(
        id=row.id, status=row.status, hands_requested=row.hands_requested,
        hands_completed=row.hands_completed, error=row.error,
    )


@api_router.get("/jobs/simulations/{job_id}", response_model=JobResponse, tags=["jobs"])
def get_simulation_job(job_id: int, session: Session = Depends(get_session)) -> JobResponse:
    row = session.get(SimulationRun, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="simulation job not found")
    return _job_response(row)


@api_router.get(
    "/jobs/simulations/{job_id}/result",
    response_model=JobResultResponse,
    tags=["jobs"],
)
def get_simulation_result(
    job_id: int, session: Session = Depends(get_session)
) -> JobResultResponse:
    row = session.get(SimulationRun, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="simulation job not found")
    return JobResultResponse(**_job_response(row).model_dump(), results=json.loads(row.result_json))


@api_router.post("/jobs/simulations/{job_id}/cancel", response_model=JobResponse, tags=["jobs"])
def stop_simulation_job(job_id: int, session: Session = Depends(get_session)) -> JobResponse:
    row = session.get(SimulationRun, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="simulation job not found")
    if row.status in {"completed", "failed", "cancelled"}:
        return _job_response(row)
    cancel_run(job_id)
    row.status = "cancelling"
    session.commit()
    session.refresh(row)
    return _job_response(row)
