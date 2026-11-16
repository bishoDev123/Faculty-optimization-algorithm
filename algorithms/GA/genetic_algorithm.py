# 	Main GA execution loop
from core.models import Problem
from core.result import OptimizationResult


def run_ga(
    problem: Problem,
    config=None,
    seed: int | None = None
) -> OptimizationResult:
    pass