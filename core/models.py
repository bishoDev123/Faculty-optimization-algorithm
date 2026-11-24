# Defines courses, lecturers, rooms, groups, time slots and sessions
from dataclasses import dataclass
from dataclasses import dataclass


@dataclass
class Lecturer:
    id: str
    name: str


@dataclass
class StudentGroup:
    id: str
    name: str
    size: int


@dataclass
class Room:
    id: str
    name: str
    capacity: int


@dataclass
class Course:
    id: str
    name: str
    lecturer_id: str
    group_id: str
    weekly_hours: int
    duration: int


@dataclass
class LectureSession:
    id: str
    course_id: str
    lecturer_id: str
    group_id: str
    duration: int


@dataclass
class Assignment:
    session_id: str
    room_id: str
    day: int
    start_slot: int


# All the input data required by the optimization algorithms.
@dataclass
class Problem:
    lecturers: list[Lecturer]
    groups: list[StudentGroup]
    rooms: list[Room]
    courses: list[Course]
    sessions: list[LectureSession]
    days: list[str]
    slots_per_day: int


@dataclass
class Timetable:
    assignments: list[Assignment]