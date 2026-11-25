#Tests hard-constraint detection.

from core.constraints import find_conflicts
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


def _sample_problem() -> Problem:
    return Problem(
        lecturers=[
            Lecturer(id="L1", name="Dr. A"),
            Lecturer(id="L2", name="Dr. B"),
        ],
        groups=[
            StudentGroup(id="G1", name="CS-1", size=25),
            StudentGroup(id="G2", name="CS-2", size=20),
        ],
        rooms=[
            Room(id="R1", name="Hall 1", capacity=40),
            Room(id="R2", name="Lab 2", capacity=15),
        ],
        courses=[
            Course(id="C1", name="AI", lecturer_id="L1", group_id="G1", weekly_hours=2, duration=2),
            Course(id="C2", name="DB", lecturer_id="L2", group_id="G2", weekly_hours=1, duration=1),
        ],
        sessions=[
            LectureSession(id="S1", course_id="C1", lecturer_id="L1", group_id="G1", duration=2),
            LectureSession(id="S2", course_id="C2", lecturer_id="L2", group_id="G2", duration=1),
        ],
        days=["Sun", "Mon", "Tue", "Wed", "Thu"],
        slots_per_day=6,
    )


def test_valid_timetable_has_no_conflicts():
    problem = _sample_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),  # slots 0, 1
            Assignment(session_id="S2", room_id="R1", day=0, start_slot=2),  # slot 2 (no clash)
        ]
    )
    assert find_conflicts(timetable, problem) == []


def test_multi_slot_overlap_detected():
    problem = _sample_problem()
    # S2 uses L1 and G1 so it overlaps S1 on slot 2 even with different start slots (1 vs 2)
    overlapping_session = LectureSession(
        id="S3", course_id="C1", lecturer_id="L1", group_id="G1", duration=1
    )
    problem.sessions.append(overlapping_session)

    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=1, start_slot=1),  # occupies 1, 2
            Assignment(session_id="S3", room_id="R1", day=1, start_slot=2),  # occupies 2
        ]
    )
    violations = find_conflicts(timetable, problem)
    codes = {v.code for v in violations}
    assert "LECTURER_CONFLICT" in codes
    assert "STUDENT_GROUP_CONFLICT" in codes
    assert "ROOM_CONFLICT" in codes


def test_room_capacity_violation():
    problem = _sample_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R2", day=0, start_slot=0),  # cap 15 < size 25
        ]
    )
    violations = find_conflicts(timetable, problem)
    assert any(v.code == "ROOM_CAPACITY" for v in violations)


def test_out_of_bounds_slot():
    problem = _sample_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=5),  # 5 + 2 > 6
        ]
    )
    violations = find_conflicts(timetable, problem)
    assert any(v.code == "OUT_OF_BOUNDS" for v in violations)


def test_invalid_room_and_session():
    problem = _sample_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="NO_SUCH_ROOM", day=0, start_slot=0),
            Assignment(session_id="NO_SUCH_SESSION", room_id="R1", day=0, start_slot=1),
        ]
    )
    violations = find_conflicts(timetable, problem)
    codes = {v.code for v in violations}
    assert "INVALID_ROOM" in codes
    assert "INVALID_SESSION" in codes