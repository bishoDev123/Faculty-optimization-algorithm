# Checks lecturer, group and room conflicts
from core.models import Timetable, Problem
from core.result import ConstraintViolation


def find_conflicts(
    timetable: Timetable,
    problem: Problem
) -> list[ConstraintViolation]:
    pass