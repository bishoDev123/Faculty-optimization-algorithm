# 	Tests session generation from courses.
import pytest
from tests.utility import sample_problem
from core.session_generator import generate_sessions
from core.models import *

def test_negative_weekly_hours():
    with pytest.raises(ValueError):
        generate_sessions([
            Course("C1", "Math", "1", "2", -1, 1)
        ])


def test_negative_duration():
    with pytest.raises(ValueError):
        generate_sessions([
            Course("C1", "Math", "1", "2", 1, -1)
        ])
        
def test_generate_sessions_handles_multiple_courses():
    courses = [
        Course("C1", "Math", "L1", "G1", 4, 2),
        Course("C2", "Physics", "L2", "G2", 6, 2)
    ]

    sessions = generate_sessions(courses)

    assert len(sessions) == 5

    assert [s.id for s in sessions] == [
        "C1-S1",
        "C1-S2",
        "C2-S1",
        "C2-S2",
        "C2-S3"
    ]
    
def test_generate_sessions_copies_course_properties(sample_problem: Problem):
    course = sample_problem.courses[0]

    sessions = generate_sessions([course])

    for session in sessions:
        assert session.course_id == course.id
        assert session.lecturer_id == course.lecturer_id
        assert session.group_id == course.group_id
        assert session.duration == course.duration
        
def test_generate_sessions_returns_correct_number(sample_problem):
    sessions = generate_sessions(sample_problem.courses)
    
    assert len(sessions) == 2
