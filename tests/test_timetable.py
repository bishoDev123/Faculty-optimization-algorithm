import pytest
from core.models import Timetable, Assignment
from core.timetable import (
    create_empty_timetable,
    copy_timetable,
    get_assignments_for_session
)


# --------------------------------------------------
# 1. Create empty timetable
# --------------------------------------------------

def test_create_empty_timetable():

    timetable = create_empty_timetable()

    assert isinstance(timetable, Timetable)
    assert timetable.assignments == []


# --------------------------------------------------
# 2. Copy timetable
# --------------------------------------------------

def test_copy_timetable_preserves_assignments():

    original = Timetable(
        assignments=[
            Assignment(
                session_id="C1-S1",
                room_id="R1",
                day=0,
                start_slot=1
            )
        ]
    )

    copied = copy_timetable(original)

    assert copied == original
    assert copied is not original


def test_copy_timetable_is_independent():

    original = Timetable(
        assignments=[
            Assignment(
                session_id="C1-S1",
                room_id="R1",
                day=0,
                start_slot=1
            )
        ]
    )

    copied = copy_timetable(original)

    copied.assignments.clear()

    assert len(original.assignments) == 1
    assert len(copied.assignments) == 0


def test_copy_timetable_nested_objects_are_independent():

    original = Timetable(
        assignments=[
            Assignment(
                session_id="C1-S1",
                room_id="R1",
                day=0,
                start_slot=1
            )
        ]
    )

    copied = copy_timetable(original)

    copied.assignments[0].room_id = "R2"

    assert original.assignments[0].room_id == "R1"
    assert copied.assignments[0].room_id == "R2"


# --------------------------------------------------
# 3. Get assignments for session
# --------------------------------------------------

def test_get_assignments_for_existing_session():

    timetable = Timetable(
        assignments=[
            Assignment("C1-S1", "R1", 0, 1),
            Assignment("C1-S2", "R2", 1, 2),
            Assignment("C1-S1", "R3", 2, 3)
        ]
    )

    assignments = get_assignments_for_session(
        timetable,
        "C1-S1"
    )

    assert len(assignments) == 2

    assert all(
        assignment.session_id == "C1-S1"
        for assignment in assignments
    )


def test_get_assignments_for_nonexistent_session():

    timetable = Timetable(
        assignments=[
            Assignment("C1-S1", "R1", 0, 1)
        ]
    )

    assignments = get_assignments_for_session(
        timetable,
        "C99-S1"
    )

    assert assignments == []


def test_get_assignments_from_empty_timetable():

    timetable = create_empty_timetable()

    assignments = get_assignments_for_session(
        timetable,
        "C1-S1"
    )

    assert assignments == []
