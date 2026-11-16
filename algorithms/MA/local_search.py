# Improves individual candidate timetables
from core.models import Problem, Timetable


def improve_timetable(
    timetable: Timetable,
    problem: Problem,
    max_steps: int,
    rng
) -> Timetable:
    pass