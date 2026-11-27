from __future__ import annotations

from collections import defaultdict

from core.constraints import find_conflicts
from core.models import Assignment, LectureSession, Problem, Timetable
from core.validator import validate_timetable

DEFAULT_SOFT_WEIGHTS: dict[str, float] = {
    "hard_violation": 100.0,
    "missing_session": 50.0,
    "duplicate_session": 50.0,
    "unknown_session": 50.0,
    "lecturer_gap": 2.0,
    "group_gap": 2.0,
    "room_waste": 0.5,
}


def _count_gaps(day_slot_ranges: dict[int, list[tuple[int, int]]]) -> int:
    """Count idle slots between consecutive sessions on each day."""
    gaps = 0
    for ranges in day_slot_ranges.values():
        if len(ranges) < 2:
            continue
        sorted_ranges = sorted(ranges, key=lambda r: (r[0], r[1]))
        current_end = sorted_ranges[0][1]
        for start, end in sorted_ranges[1:]:
            if start > current_end:
                gaps += start - current_end
            if end > current_end:
                current_end = end
    return gaps


def calculate_fitness(
    timetable: Timetable,
    problem: Problem,
    soft_weights: dict[str, float] | None = None,
) -> float:
    """Calculate a quality score for a timetable (higher is better; 0.0 is ideal)."""
    weights = {**DEFAULT_SOFT_WEIGHTS, **(soft_weights or {})}

    validation = validate_timetable(timetable, problem)
    conflicts = find_conflicts(timetable, problem)

    sessions_by_id: dict[str, LectureSession] = {
        s.id: s for s in problem.sessions
    }
    rooms_by_id = {r.id: r for r in problem.rooms}
    groups_by_id = {g.id: g for g in problem.groups}

    known_assignment_ids = {a.session_id for a in timetable.assignments}
    unknown_session_count = sum(
        1 for sid in known_assignment_ids if sid not in sessions_by_id
    )

    lecturer_day_ranges: dict[str, dict[int, list[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    group_day_ranges: dict[str, dict[int, list[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    room_waste_slots = 0

    for assignment in timetable.assignments:
        session = sessions_by_id.get(assignment.session_id)
        if session is None:
            continue

        start = assignment.start_slot
        end = assignment.start_slot + session.duration
        lecturer_day_ranges[session.lecturer_id][assignment.day].append((start, end))
        group_day_ranges[session.group_id][assignment.day].append((start, end))

        room = rooms_by_id.get(assignment.room_id)
        group = groups_by_id.get(session.group_id)
        if room is not None and group is not None and room.capacity > group.size:
            room_waste_slots += (room.capacity - group.size) * session.duration

    lecturer_gaps = sum(
        _count_gaps(day_map) for day_map in lecturer_day_ranges.values()
    )
    group_gaps = sum(
        _count_gaps(day_map) for day_map in group_day_ranges.values()
    )

    hard_count = len(conflicts) if conflicts else len(validation.hard_violations)

    penalty = (
        hard_count * weights["hard_violation"]
        + len(validation.missing_session_ids) * weights["missing_session"]
        + len(validation.duplicate_session_ids) * weights["duplicate_session"]
        + unknown_session_count * weights["unknown_session"]
        + lecturer_gaps * weights["lecturer_gap"]
        + group_gaps * weights["group_gap"]
        + room_waste_slots * weights["room_waste"]
    )

    return -float(penalty)