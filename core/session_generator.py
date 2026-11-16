# Converts course requirements into individual teaching sessions
from core.models import Course, LectureSession


def generate_sessions(courses: list[Course]) -> list[LectureSession]:
    pass