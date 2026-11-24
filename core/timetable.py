
from copy import deepcopy

from core.models import Timetable, Assignment


def create_empty_timetable() -> Timetable:
    """Create a timetable without any assignments."""

    return Timetable(assignments=[])


def copy_timetable(timetable: Timetable) -> Timetable:
    """
    Create an independent copy of a timetable.

    Changes to the copied timetable must not affect
    the original timetable.
    """

    return deepcopy(timetable)


def get_assignments_for_session(
    timetable: Timetable,
    session_id: str
) -> list[Assignment]:
    """Return all assignments belonging to a session."""

    return [
        assignment
        for assignment in timetable.assignments
        if assignment.session_id == session_id
    ]
