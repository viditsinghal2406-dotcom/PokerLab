from app.experiments import run_experiment
from app.schemas.experiments import ExperimentRequest


def test_experiment_uses_common_seeds_and_returns_confidence_intervals():
    request = ExperimentRequest(name="comparison", kind="E", trials=3, hands=4, seed_start=100)
    seeds, results = run_experiment(request)
    assert seeds == [100, 101, 102]
    assert len(results) == 4
    assert all(result.observations == 12 for result in results)
    assert all(result.ci95 is not None for result in results)


def test_vidit_parameter_experiment_returns_distinct_comparison_labels():
    request = ExperimentRequest(name="sensitivity", kind="B", trials=1, hands=3)
    _, results = run_experiment(request)
    assert [result.label for result in results] == [
        "Vidit low aggression", "Vidit default", "Vidit high aggression"
    ]
