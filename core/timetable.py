# 	Represents a candidate timetable
from core.models import Timetable


def create_empty_timetable() -> Timetable:
    pass


def copy_timetable(timetable: Timetable) -> Timetable:
    pass


def get_assignments_for_session(timetable: Timetable, session_id: int):
    pass