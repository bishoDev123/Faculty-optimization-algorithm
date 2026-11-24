# Load and validate a scheduling problem from a JSON file.

import json

from pathlib import Path

from core.models import (
    Lecturer,
    StudentGroup,
    Room,
    Course,
    Problem
)

from core.session_generator import generate_sessions
from core.problem import validate_problem_data


def load_problem(path: str) -> Problem:

    file_path = Path(path)

    # checks to see if the file was there
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    # reads the file and sees if the JSON is valid
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {file_path}: {error}"
        ) from error

    # checks if the data is decoded from JSON to a dictionary
    if not isinstance(data, dict):
        raise ValueError("Dataset root must be a JSON object")

    # checks for any missing components in the file
    required_keys = {
        "lecturers",
        "groups",
        "rooms",
        "courses",
        "days",
        "slots_per_day"
    }

    missing_keys = required_keys - data.keys()

    if missing_keys:
        raise ValueError(
            f"Missing required dataset keys: {sorted(missing_keys)}"
        )

    # creates objects from core.models using the file data
    try:
        lecturers = [
            Lecturer(**item)
            for item in data["lecturers"]
        ]

        groups = [
            StudentGroup(**item)
            for item in data["groups"]
        ]

        rooms = [
            Room(**item)
            for item in data["rooms"]
        ]

        courses = [
            Course(**item)
            for item in data["courses"]
        ]

        if not isinstance(data["days"], list):
            raise ValueError("'days' must be a list")

        if not isinstance(data["slots_per_day"], int) or isinstance(
            data["slots_per_day"], bool
        ):
            raise ValueError("'slots_per_day' must be an integer")

        sessions = generate_sessions(courses)

        problem = Problem(
            lecturers=lecturers,
            groups=groups,
            rooms=rooms,
            courses=courses,
            sessions=sessions,
            days=data["days"],
            slots_per_day=data["slots_per_day"]
        )

    # checks if any of the values of the file don't match the models
    except (TypeError, KeyError) as error:
        raise ValueError(
            f"Invalid dataset structure: {error}"
        ) from error

    result = validate_problem_data(problem)


    if not result.is_valid:
        errors = "\n".join(
            f"[{violation.code}] {violation.message}"
            for violation in result.hard_violations
        )

        raise ValueError(
            f"Dataset validation failed:\n{errors}"
        )

    return problem
