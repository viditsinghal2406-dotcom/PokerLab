from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.db.models import Hand, SimulationRun
from app.db.session import SessionLocal
from app.simulation.engine import OmahaVariant, play_multiway_hand

MAX_HANDS = 10_000
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pokerlab")
cancel_events: dict[int, threading.Event] = {}


def start_run(seed: int, variant: str, player_count: int, hands: int) -> int:
    if hands < 1 or hands > MAX_HANDS:
        raise ValueError(f"hands must be between 1 and {MAX_HANDS}")
    with SessionLocal() as session:
        run = SimulationRun(
            status="queued", seed=seed, variant=variant, player_count=player_count,
            hands_requested=hands,
        )
        session.add(run)
        session.commit()
        run_id = run.id
    cancel_events[run_id] = threading.Event()
    executor.submit(_run, run_id)
    return run_id


def cancel_run(run_id: int) -> bool:
    event = cancel_events.get(run_id)
    if event is None:
        return False
    event.set()
    return True


def _run(run_id: int) -> None:
    with SessionLocal() as session:
        run = session.get(SimulationRun, run_id)
        if run is None:
            return
        run.status = "running"
        session.commit()
        event = cancel_events[run_id]
        results: list[dict] = []
        try:
            for index in range(run.hands_requested):
                if event.is_set():
                    run.status = "cancelled"
                    break
                result = play_multiway_hand(
                    run.seed + index, run.player_count, OmahaVariant(run.variant)
                )
                serialized = {
                    "winners": list(result.winners),
                    "stacks": result.stacks,
                    "board": [str(card) for card in result.board],
                }
                results.append(serialized)
                session.add(Hand(run_id=run.id, seed=run.seed + index, result_json=json.dumps(serialized)))
                run.hands_completed = index + 1
                if index % 10 == 0:
                    session.commit()
            else:
                run.status = "completed"
            run.result_json = json.dumps(results)
            run.completed_at = datetime.now(timezone.utc)
            session.commit()
        except Exception as exc:
            run.status = "failed"
            run.error = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            session.commit()
        finally:
            cancel_events.pop(run_id, None)
