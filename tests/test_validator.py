from core.models import (
    Assignment,
    Course,
    LectureSession,
    Lecturer,
    Problem,
    Room,
    StudentGroup,
    Timetable,
)
from core.validator import validate_timetable


def _make_problem() -> Problem:
    lecturers = [
        Lecturer(id="L1", name="Dr. Ahmed"),
        Lecturer(id="L2", name="Dr. Sara"),
    ]
    groups = [
        StudentGroup(id="G1", name="Group 1", size=30),
        StudentGroup(id="G2", name="Group 2", size=15),
    ]
    rooms = [
        Room(id="R1", name="Hall 1", capacity=50),
        Room(id="R2", name="Lab 2", capacity=20),
    ]
    courses = [
        Course(id="C1", name="Algorithms", lecturer_id="L1", group_id="G1", weekly_hours=2, duration=1),
        Course(id="C2", name="Databases", lecturer_id="L2", group_id="G2", weekly_hours=2, duration=1),
        Course(id="C3", name="Operating Systems", lecturer_id="L1", group_id="G2", weekly_hours=2, duration=1),
    ]
            
    sessions = [
        LectureSession(id="S1", course_id="C1", lecturer_id="L1", group_id="G1", duration=1),
        LectureSession(id="S2", course_id="C2", lecturer_id="L2", group_id="G2", duration=1),
        LectureSession(id="S3", course_id="C3", lecturer_id="L1", group_id="G2", duration=1),
    ]
    return Problem(
        lecturers=lecturers,
        groups=groups,
        rooms=rooms,
        courses=courses,
        sessions=sessions,
        days=["Sun", "Mon", "Tue", "Wed", "Thu"],
        slots_per_day=6,
    )


def test_valid_complete_timetable():
    problem = _make_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R2", day=0, start_slot=1),
            Assignment(session_id="S3", room_id="R1", day=1, start_slot=0),
        ]
    )

    result = validate_timetable(timetable, problem)

    assert result.is_valid is True
    assert result.hard_violations == []
    assert result.missing_session_ids == []
    assert result.duplicate_session_ids == []


def test_missing_and_duplicate_sessions():
    problem = _make_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S1", room_id="R1", day=1, start_slot=0),
            Assignment(session_id="S2", room_id="R2", day=0, start_slot=1),
        ]
    )

    result = validate_timetable(timetable, problem)

    assert result.is_valid is False
    assert "S3" in result.missing_session_ids
    assert "S1" in result.duplicate_session_ids


def test_all_sessions_present_but_has_conflict():
    problem = _make_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R2", day=0, start_slot=1),
            Assignment(session_id="S3", room_id="R2", day=0, start_slot=0),
        ]
    )

    result = validate_timetable(timetable, problem)

    assert result.is_valid is False
    assert len(result.hard_violations) > 0
    assert result.missing_session_ids == []
    assert result.duplicate_session_ids == []