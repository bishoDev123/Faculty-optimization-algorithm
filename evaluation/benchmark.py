# Runs GA and MA under comparable conditions
from core.models import Problem
from core.result import OptimizationResult


def run_comparison(
    problem: Problem,
    ga_config,
    ma_config,
    seeds: list[int]
) -> dict[str, list[OptimizationResult]]:
    pass