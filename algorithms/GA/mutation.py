# 	Randomly changes timetable assignments
from core.models import Problem, Timetable


def mutate(
    timetable: Timetable,
    problem: Problem,
    rng,
    mutation_rate: float
) -> Timetable:
    pass