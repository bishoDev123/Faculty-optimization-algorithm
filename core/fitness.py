# 	Calculates the quality score of a timetable

from core.models import Timetable, Problem


def calculate_fitness(
    timetable: Timetable,
    problem: Problem,
    soft_weights: dict | None = None
):
    pass