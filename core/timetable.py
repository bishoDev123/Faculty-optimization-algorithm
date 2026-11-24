
from copy import deepcopy

from core.models import Timetable, Assignment


def create_empty_timetable() -> Timetable:
    return Timetable(assignments=[])


def copy_timetable(timetable: Timetable) -> Timetable:
    return deepcopy(timetable)


# Return all assignments belonging to a session
def get_assignments_for_session(
    timetable: Timetable,
    session_id: str
) -> list[Assignment]:

    return [
        assignment
        for assignment in timetable.assignments
        if assignment.session_id == session_id
    ]
