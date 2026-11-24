import pytest
from core.models import *

@pytest.fixture
def sample_problem() -> Problem:
    lecturers = [Lecturer(id="L1", name="Dr. Smith")]
    groups = [StudentGroup(id="G1", name="CS-101", size=30)]
    rooms = [Room(id="R1", name="Hall A", capacity=40)]
    courses = [
        Course(
            id="C1",
            name="Algorithms",
            lecturer_id="L1",
            group_id="G1",
            weekly_hours=4,
            duration=2,
        )
    ]
    sessions = [
        LectureSession(id="S1", course_id="C1", lecturer_id="L1", group_id="G1", duration=2),
        LectureSession(id="S2", course_id="C1", lecturer_id="L1", group_id="G1", duration=2),
    ]
    return Problem(
        lecturers=lecturers,
        groups=groups,
        rooms=rooms,
        courses=courses,
        sessions=sessions,
        days=["Mon", "Tue", "Wed", "Thu", "Fri"],
        slots_per_day=8,
    )