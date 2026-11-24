
import json
import pytest

from pathlib import Path

from data.datasets import load_problem
from core.models import Problem


EXAMPLE_DATASET = (
    Path(__file__).parent.parent
    / "data"
    / "raw"
    / "input_example.json"
)


# --------------------------------------------------
# 1. Load valid dataset
# --------------------------------------------------

def test_load_valid_dataset():

    problem = load_problem(str(EXAMPLE_DATASET))

    assert isinstance(problem, Problem)

    assert len(problem.lecturers) == 4
    assert len(problem.groups) == 3
    assert len(problem.rooms) == 4
    assert len(problem.courses) == 6
    assert len(problem.sessions) == 14


# --------------------------------------------------
# 2. Check generated sessions
# --------------------------------------------------

def test_load_generates_correct_sessions():

    problem = load_problem(str(EXAMPLE_DATASET))

    session_ids = {
        session.id
        for session in problem.sessions
    }

    assert len(session_ids) == 14

    assert "C1-S1" in session_ids
    assert "C1-S2" in session_ids
    assert "C2-S1" in session_ids
    assert "C2-S2" in session_ids


# --------------------------------------------------
# 3. Check session references
# --------------------------------------------------

def test_generated_sessions_have_correct_references():

    problem = load_problem(str(EXAMPLE_DATASET))

    courses = {
        course.id: course
        for course in problem.courses
    }

    for session in problem.sessions:

        course = courses[session.course_id]

        assert session.lecturer_id == course.lecturer_id
        assert session.group_id == course.group_id
        assert session.duration == course.duration


# --------------------------------------------------
# 4. File not found
# --------------------------------------------------

def test_missing_dataset_file():

    with pytest.raises(FileNotFoundError):

        load_problem("data/raw/nonexistent.json")


# --------------------------------------------------
# 5. Invalid JSON
# --------------------------------------------------

def test_malformed_json(tmp_path):

    file_path = tmp_path / "invalid.json"

    file_path.write_text(
        '{"lecturers": [invalid json]}',
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Invalid JSON"):

        load_problem(str(file_path))


# --------------------------------------------------
# 6. Invalid root structure
# --------------------------------------------------

@pytest.mark.parametrize(
    "content",
    [
        "[]",
        '"invalid"',
        "null",
        "123"
    ]
)
def test_invalid_json_root(tmp_path, content):

    file_path = tmp_path / "invalid.json"

    file_path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="root"):

        load_problem(str(file_path))


# --------------------------------------------------
# 7. Missing required keys
# --------------------------------------------------

def test_missing_required_keys(tmp_path):

    data = {
        "lecturers": [],
        "groups": []
    }

    file_path = tmp_path / "missing_keys.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Missing required"):

        load_problem(str(file_path))


# --------------------------------------------------
# 8. Invalid dataclass fields
# --------------------------------------------------

def test_invalid_lecturer_structure(tmp_path):

    data = {
        "days": ["Sunday"],
        "slots_per_day": 6,

        "lecturers": [
            {
                "id": "L1"
                # Missing name
            }
        ],

        "groups": [],
        "rooms": [],
        "courses": []
    }

    file_path = tmp_path / "invalid_lecturer.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Invalid dataset structure"):

        load_problem(str(file_path))


# --------------------------------------------------
# 9. Invalid lecturer reference
# --------------------------------------------------

def test_dataset_with_invalid_lecturer_reference(tmp_path):

    data = {
        "days": ["Sunday"],
        "slots_per_day": 6,

        "lecturers": [
            {"id": "L1", "name": "Ahmed"}
        ],

        "groups": [
            {"id": "G1", "name": "Group 1", "size": 30}
        ],

        "rooms": [
            {"id": "R1", "name": "Room 1", "capacity": 40}
        ],

        "courses": [
            {
                "id": "C1",
                "name": "Math",
                "lecturer_id": "L99",
                "group_id": "G1",
                "weekly_hours": 2,
                "duration": 1
            }
        ]
    }

    file_path = tmp_path / "invalid_reference.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    with pytest.raises(
        ValueError,
        match="INVALID_LECTURER_REFERENCE"
    ):

        load_problem(str(file_path))


# --------------------------------------------------
# 10. Invalid course requirements
# --------------------------------------------------

def test_dataset_with_invalid_course_duration(tmp_path):

    data = {
        "days": ["Sunday"],
        "slots_per_day": 6,

        "lecturers": [
            {"id": "L1", "name": "Ahmed"}
        ],

        "groups": [
            {"id": "G1", "name": "Group 1", "size": 30}
        ],

        "rooms": [
            {"id": "R1", "name": "Room 1", "capacity": 40}
        ],

        "courses": [
            {
                "id": "C1",
                "name": "Math",
                "lecturer_id": "L1",
                "group_id": "G1",
                "weekly_hours": 3,
                "duration": 2
            }
        ]
    }

    file_path = tmp_path / "invalid_course.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    with pytest.raises(
        ValueError,
        match="Invalid weekly hours with the duration of C1"
    ):

        load_problem(str(file_path))


# --------------------------------------------------
# 11. Invalid days structure
# --------------------------------------------------

def test_invalid_days_structure(tmp_path):

    data = {
        "days": "Sunday",
        "slots_per_day": 6,
        "lecturers": [],
        "groups": [],
        "rooms": [],
        "courses": []
    }

    file_path = tmp_path / "invalid_days.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="'days' must be a list"):

        load_problem(str(file_path))


# --------------------------------------------------
# 12. Invalid slots type
# --------------------------------------------------

@pytest.mark.parametrize("slots", ["6", 6.5, True])

def test_invalid_slots_type(tmp_path, slots):

    data = {
        "days": ["Sunday"],
        "slots_per_day": slots,
        "lecturers": [],
        "groups": [],
        "rooms": [],
        "courses": []
    }

    file_path = tmp_path / "invalid_slots.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    with pytest.raises(
        ValueError,
        match="'slots_per_day' must be an integer"
    ):

        load_problem(str(file_path))
