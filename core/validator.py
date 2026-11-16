# 	Checks whether a timetable is valid and complete
from core.models import Timetable, Problem
from core.result import ValidationResult


def validate_timetable(
    timetable: Timetable,
    problem: Problem
) -> ValidationResult:
    pass