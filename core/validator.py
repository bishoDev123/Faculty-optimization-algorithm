# Checks whether a timetable is valid and complete
from collections import Counter

from core.constraints import find_conflicts
from core.models import Problem, Timetable
from core.result import ValidationResult


def validate_timetable(
    timetable: Timetable,
    problem: Problem,
) -> ValidationResult:
    violations = find_conflicts(timetable, problem)
    hard_violations = [v for v in violations if v.severity == "hard"]

    expected_ids = [session.id for session in problem.sessions]
    assigned_ids = [assignment.session_id for assignment in timetable.assignments]
    counts = Counter(assigned_ids)
    assigned_set = set(assigned_ids)

    missing_session_ids = [
        session_id for session_id in expected_ids if session_id not in assigned_set
    ]

    duplicate_session_ids: list[str] = []
    seen_duplicates: set[str] = set()
    for session_id in assigned_ids:
        if counts[session_id] > 1 and session_id not in seen_duplicates:
            seen_duplicates.add(session_id)
            duplicate_session_ids.append(session_id)

    is_valid = (
        len(hard_violations) == 0
        and len(missing_session_ids) == 0
        and len(duplicate_session_ids) == 0
    )

    return ValidationResult(
        is_valid=is_valid,
        hard_violations=hard_violations,
        missing_session_ids=missing_session_ids,
        duplicate_session_ids=duplicate_session_ids,
    )