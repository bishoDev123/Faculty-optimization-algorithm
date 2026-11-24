
import pytest
from dataclasses import replace

from core.models import (
    Lecturer,
    StudentGroup,
    Room,
    Course,
    LectureSession,
    Problem
)

from core.problem import validate_problem_data


# --------------------------------------------------
# Test data factory
# --------------------------------------------------

def make_problem(
    lecturers=None,
    groups=None,
    rooms=None,
    courses=None,
    sessions=None,
    days=None,
    slots_per_day=6
) -> Problem:

    lecturers = lecturers if lecturers is not None else [
        Lecturer(id="L1", name="Ahmed")
    ]

    groups = groups if groups is not None else [
        StudentGroup(id="G1", name="CS-Year-1", size=30)
    ]

    rooms = rooms if rooms is not None else [
        Room(id="R1", name="Room 101", capacity=40)
    ]

    courses = courses if courses is not None else [
        Course(
            id="C1",
            name="Mathematics",
            lecturer_id="L1",
            group_id="G1",
            weekly_hours=2,
            duration=1
        )
    ]

    sessions = sessions if sessions is not None else [
        LectureSession(
            id="C1-S1",
            course_id="C1",
            lecturer_id="L1",
            group_id="G1",
            duration=1
        ),
        LectureSession(
            id="C1-S2",
            course_id="C1",
            lecturer_id="L1",
            group_id="G1",
            duration=1
        )
    ]

    days = days if days is not None else [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday"
    ]

    return Problem(
        lecturers=lecturers,
        groups=groups,
        rooms=rooms,
        courses=courses,
        sessions=sessions,
        days=days,
        slots_per_day=slots_per_day
    )


def get_violation_codes(result):
    return {violation.code for violation in result.hard_violations}


# --------------------------------------------------
# 1. Valid problem
# --------------------------------------------------

def test_valid_problem_returns_valid_result():

    problem = make_problem()

    result = validate_problem_data(problem)

    assert result.is_valid is True
    assert result.hard_violations == []


# --------------------------------------------------
# 2. Unique ID validation
# --------------------------------------------------

def test_duplicate_lecturer_id():

    problem = make_problem(
        lecturers=[
            Lecturer(id="L1", name="Ahmed"),
            Lecturer(id="L1", name="Mohamed")
        ]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "DUPLICATE_ID" in get_violation_codes(result)


def test_duplicate_session_id():

    problem = make_problem(
        sessions=[
            LectureSession(
                id="C1-S1",
                course_id="C1",
                lecturer_id="L1",
                group_id="G1",
                duration=1
            ),
            LectureSession(
                id="C1-S1",
                course_id="C1",
                lecturer_id="L1",
                group_id="G1",
                duration=1
            )
        ]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "DUPLICATE_ID" in get_violation_codes(result)


# --------------------------------------------------
# 3. Lecturer reference validation
# --------------------------------------------------

def test_invalid_lecturer_reference():

    course = Course(
        id="C1",
        name="Mathematics",
        lecturer_id="L99",
        group_id="G1",
        weekly_hours=2,
        duration=1
    )

    problem = make_problem(courses=[course])

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_LECTURER_REFERENCE" in get_violation_codes(result)


# --------------------------------------------------
# 4. Student group reference validation
# --------------------------------------------------

def test_invalid_group_reference():

    course = Course(
        id="C1",
        name="Mathematics",
        lecturer_id="L1",
        group_id="G99",
        weekly_hours=2,
        duration=1
    )

    problem = make_problem(courses=[course])

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_GROUP_REFERENCE" in get_violation_codes(result)


# --------------------------------------------------
# 5. Room capacity validation
# --------------------------------------------------

def test_invalid_room_capacity():

    problem = make_problem(
        rooms=[
            Room(id="R1", name="Room 101", capacity=0)
        ]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_ROOM_CAPACITY" in get_violation_codes(result)


# --------------------------------------------------
# 6. Student group size validation
# --------------------------------------------------

def test_invalid_group_size():

    problem = make_problem(
        groups=[
            StudentGroup(id="G1", name="CS-Year-1", size=-5)
        ]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_GROUP_SIZE" in get_violation_codes(result)


# --------------------------------------------------
# 7. Course requirements validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "weekly_hours,duration,expected_code",
    [
        (0, 1, "INVALID_WEEKLY_HOURS"),
        (-2, 1, "INVALID_WEEKLY_HOURS"),
        (2, 0, "INVALID_COURSE_DURATION"),
        (4, -1, "INVALID_COURSE_DURATION"),
        (3, 2, "INCOMPATIBLE_COURSE_DURATION")
    ]
)
def test_invalid_course_requirements(
    weekly_hours,
    duration,
    expected_code
):

    course = Course(
        id="C1",
        name="Mathematics",
        lecturer_id="L1",
        group_id="G1",
        weekly_hours=weekly_hours,
        duration=duration
    )

    problem = make_problem(courses=[course], sessions=[])

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert expected_code in get_violation_codes(result)


# --------------------------------------------------
# 8. Timetable configuration validation
# --------------------------------------------------

def test_no_available_days():

    problem = make_problem(days=[])

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "NO_AVAILABLE_DAYS" in get_violation_codes(result)


def test_duplicate_days():

    problem = make_problem(
        days=["Sunday", "Monday", "Sunday"]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "DUPLICATE_DAYS" in get_violation_codes(result)


def test_invalid_slots_per_day():

    problem = make_problem(slots_per_day=0)

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_SLOTS_PER_DAY" in get_violation_codes(result)


# --------------------------------------------------
# 9. Session course reference validation
# --------------------------------------------------

def test_session_references_nonexistent_course():

    session = LectureSession(
        id="C99-S1",
        course_id="C99",
        lecturer_id="L1",
        group_id="G1",
        duration=1
    )

    problem = make_problem(sessions=[session])

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_SESSION_COURSE" in get_violation_codes(result)


# --------------------------------------------------
# 10. Session attribute consistency
# --------------------------------------------------

def test_session_lecturer_mismatch():

    session = LectureSession(
        id="C1-S1",
        course_id="C1",
        lecturer_id="L99",
        group_id="G1",
        duration=1
    )

    problem = make_problem(sessions=[session])

    result = validate_problem_data(problem)

    assert "SESSION_LECTURER_MISMATCH" in get_violation_codes(result)


def test_session_group_mismatch():

    session = LectureSession(
        id="C1-S1",
        course_id="C1",
        lecturer_id="L1",
        group_id="G99",
        duration=1
    )

    problem = make_problem(sessions=[session])

    result = validate_problem_data(problem)

    assert "SESSION_GROUP_MISMATCH" in get_violation_codes(result)


def test_session_duration_mismatch():

    session = LectureSession(
        id="C1-S1",
        course_id="C1",
        lecturer_id="L1",
        group_id="G1",
        duration=2
    )

    problem = make_problem(sessions=[session])

    result = validate_problem_data(problem)

    assert "SESSION_DURATION_MISMATCH" in get_violation_codes(result)


def test_invalid_session_duration():

    session = LectureSession(
        id="C1-S1",
        course_id="C1",
        lecturer_id="L1",
        group_id="G1",
        duration=0
    )

    problem = make_problem(sessions=[session])

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INVALID_SESSION_DURATION" in get_violation_codes(result)


# --------------------------------------------------
# 11. Expected session count validation
# --------------------------------------------------

def test_missing_generated_session():

    problem = make_problem(
        sessions=[
            LectureSession(
                id="C1-S1",
                course_id="C1",
                lecturer_id="L1",
                group_id="G1",
                duration=1
            )
        ]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INCORRECT_SESSION_COUNT" in get_violation_codes(result)


def test_excess_generated_sessions():

    problem = make_problem(
        sessions=[
            LectureSession(
                id="C1-S1",
                course_id="C1",
                lecturer_id="L1",
                group_id="G1",
                duration=1
            ),
            LectureSession(
                id="C1-S2",
                course_id="C1",
                lecturer_id="L1",
                group_id="G1",
                duration=1
            ),
            LectureSession(
                id="C1-S3",
                course_id="C1",
                lecturer_id="L1",
                group_id="G1",
                duration=1
            )
        ]
    )

    result = validate_problem_data(problem)

    assert result.is_valid is False
    assert "INCORRECT_SESSION_COUNT" in get_violation_codes(result)
