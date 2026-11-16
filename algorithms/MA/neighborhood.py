# 	Generates possible modifications to a timetable
from core.models import Problem, Timetable


def generate_neighbors(
    timetable: Timetable,
    problem: Problem,
    rng,
    max_neighbors: int = 20
) -> list[Timetable]:
    pass