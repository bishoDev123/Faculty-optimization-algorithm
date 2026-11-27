# 	Tests fitness calculations.

from core.fitness import calculate_fitness
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


def _make_problem() -> Problem:
    lecturers = [
        Lecturer(id="L1", name="Dr. Ahmed"),
        Lecturer(id="L2", name="Dr. Sara"),
    ]
    groups = [
        StudentGroup(id="G1", name="Group 1", size=30),
        StudentGroup(id="G2", name="Group 2", size=20),
    ]
    rooms = [
        Room(id="R1", name="Hall 1", capacity=30),
        Room(id="R2", name="Lab 2", capacity=20),
        Room(id="R3", name="Auditorium", capacity=50),
    ]
    courses = [
        Course(id="C1", name="Algorithms", lecturer_id="L1", group_id="G1", weekly_hours=2, duration=1),
        Course(id="C2", name="Databases", lecturer_id="L2", group_id="G2", weekly_hours=2, duration=1),
    ]
    sessions = [
        LectureSession(id="S1", course_id="C1", lecturer_id="L1", group_id="G1", duration=1),
        LectureSession(id="S2", course_id="C1", lecturer_id="L1", group_id="G1", duration=1),
        LectureSession(id="S3", course_id="C2", lecturer_id="L2", group_id="G2", duration=1),
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


def test_ideal_timetable_scores_zero():
    problem = _make_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R1", day=0, start_slot=1),
            Assignment(session_id="S3", room_id="R2", day=0, start_slot=0),
        ]
    )

    assert calculate_fitness(timetable, problem) == 0.0


def test_gaps_and_room_waste_lower_score():
    problem = _make_problem()

    compact = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R1", day=0, start_slot=1),
            Assignment(session_id="S3", room_id="R2", day=0, start_slot=0),
        ]
    )
    # S1 at slot 0, S2 at slot 2 -> 1 gap for L1 and 1 gap for G1; S3 in R3 (cap 50 vs size 20) -> 30 waste
    gapped_and_oversized = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R1", day=0, start_slot=2),
            Assignment(session_id="S3", room_id="R3", day=0, start_slot=0),
        ]
    )

    score_compact = calculate_fitness(compact, problem)
    score_gapped = calculate_fitness(gapped_and_oversized, problem)

    assert score_gapped < score_compact == 0.0


def test_custom_soft_weights_affect_score():
    problem = _make_problem()
    timetable = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R1", day=0, start_slot=2),
            Assignment(session_id="S3", room_id="R2", day=0, start_slot=0),
        ]
    )

    default_score = calculate_fitness(timetable, problem)
    heavy_gap_score = calculate_fitness(
        timetable,
        problem,
        soft_weights={"lecturer_gap": 10.0, "group_gap": 10.0},
    )

    assert heavy_gap_score < default_score


def test_hard_violation_or_missing_session_heavily_penalized():
    problem = _make_problem()
    # S1 and S2 overlap for L1/G1/R1 at day=0, slot=0, and S3 is missing
    broken = Timetable(
        assignments=[
            Assignment(session_id="S1", room_id="R1", day=0, start_slot=0),
            Assignment(session_id="S2", room_id="R1", day=0, start_slot=0),
        ]
    )

    score = calculate_fitness(broken, problem)

    assert score <= -150.0