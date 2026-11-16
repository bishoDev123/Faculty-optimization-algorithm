# 	Combines two parent timetables
from core.models import Timetable


def crossover(
    parent_a: Timetable,
    parent_b: Timetable,
    rng
) -> tuple[Timetable, Timetable]:
    pass