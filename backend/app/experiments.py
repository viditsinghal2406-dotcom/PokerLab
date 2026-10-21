from __future__ import annotations

import math
from dataclasses import dataclass

from app.simulation.engine import OmahaVariant, play_multiway_hand
from app.simulation.policies import POLICIES, DecisionContext, PolicyConfig, decide


@dataclass(frozen=True)
class ExperimentMetric:
    label: str
    mean_bb_per_hand: float
    ci95: float | None
    sd_bb_per_hand: float | None
    average_max_drawdown: float
    biggest_win: float
    observations: int


def _sample_sd(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def _metric(label: str, trial_values: list[float], drawdowns: list[float], wins: list[float], hands: int) -> ExperimentMetric:
    mean = sum(trial_values) / len(trial_values)
    sd = _sample_sd(trial_values)
    ci95 = 1.96 * sd / math.sqrt(len(trial_values)) if sd is not None else None
    return ExperimentMetric(
        label, mean / hands, ci95 / hands if ci95 is not None else None,
        sd / hands if sd is not None else None,
        sum(drawdowns) / len(drawdowns), max(wins), len(trial_values) * hands,
    )


def _conditions(kind: str, variant: str) -> list[tuple[str, str, str]]:
    if kind in {"A", "E"}:
        return [(name.title(), name, variant) for name in ("vidit", "aggressive", "balanced", "conservative")]
    if kind == "B":
        return [("Vidit low aggression", "vidit-low", variant), ("Vidit default", "vidit", variant),
                ("Vidit high aggression", "vidit-high", variant)]
    if kind == "C":
        return [(name.title(), name, variant) for name in POLICIES]
    if kind in {"D", "F"}:
        return [("Hold'em", "vidit", "holdem"), ("Omaha", "vidit", "omaha"),
                ("5-Card Omaha", "vidit", "omaha5"), ("Pineapple", "vidit", "pineapple")]
    raise ValueError("unsupported experiment kind")


def _policy(name: str, request) -> PolicyConfig:
    base = POLICIES["vidit" if name.startswith("vidit") else name]
    if name == "vidit-low":
        return PolicyConfig(base.name, 0.2, base.bluff, base.risk)
    if name == "vidit-high":
        return PolicyConfig(base.name, 1.0, base.bluff, base.risk)
    if name == "vidit":
        return PolicyConfig(base.name, request.aggression, request.bluff, request.risk)
    return base


def run_experiment(request) -> tuple[list[int], list[ExperimentMetric]]:
    seeds = [request.seed_start + index for index in range(request.trials)]
    results: list[ExperimentMetric] = []
    for label, policy_name, condition_variant in _conditions(request.kind, request.variant):
        trial_values: list[float] = []
        drawdowns: list[float] = []
        biggest_wins: list[float] = []
        for seed in seeds:
            profit = 0.0
            peak = 0.0
            max_drawdown = 0.0
            biggest_win = 0.0
            policy = _policy(policy_name, request)
            engine_variant = OmahaVariant(condition_variant)
            for offset in range(request.hands):
                hand_seed = seed + offset
                result = play_multiway_hand(hand_seed, 2, engine_variant, folded=set())
                decision = decide(
                    policy,
                    DecisionContext(
                        engine_variant, tuple(result.hole[0]), tuple(result.board),
                        sum(result.contributions), 0, 1, 100, True,
                    ),
                    hand_seed,
                )
                if decision.kind == "fold":
                    result = play_multiway_hand(hand_seed, 2, engine_variant, folded={0})
                change = result.stacks[0] - 100.0
                profit += change
                peak = max(peak, profit)
                max_drawdown = max(max_drawdown, peak - profit)
                biggest_win = max(biggest_win, change)
            trial_values.append(profit)
            drawdowns.append(max_drawdown)
            biggest_wins.append(biggest_win)
        results.append(_metric(label, trial_values, drawdowns, biggest_wins, request.hands))
    return seeds, results
