# 	Executes repeated trials with different random seeds
from core.models import Problem
from core.result import OptimizationResult


def run_experiment(
    problem: Problem,
    algorithm: str,
    config,
    seeds: list[int]
) -> list[OptimizationResult]:
    pass