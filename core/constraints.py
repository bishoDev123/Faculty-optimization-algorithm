# Checks lecturer, group and room conflicts
from core.models import Timetable, Problem
from core.result import ConstraintViolation


def _occupied_slots(start_slot: int, duration: int) -> range:
    """Return all slot indices occupied by a session."""
    return range(start_slot, start_slot + duration)


def find_conflicts(
    timetable: Timetable,
    problem: Problem
) -> list[ConstraintViolation]:
    violations: list[ConstraintViolation] = []

    sessions_by_id = {s.id: s for s in problem.sessions}
    rooms_by_id = {r.id: r for r in problem.rooms}
    groups_by_id = {g.id: g for g in problem.groups}
    lecturers_by_id = {l.id: l for l in problem.lecturers}

    # Map (entity_id, day, slot) -> first session_id occupying that slot
    lecturer_slots: dict[tuple[str, int, int], str] = {}
    group_slots: dict[tuple[str, int, int], str] = {}
    room_slots: dict[tuple[str, int, int], str] = {}

    num_days = len(problem.days)
    slots_per_day = problem.slots_per_day

    for assignment in timetable.assignments:
        # 1. Validate session reference
        session = sessions_by_id.get(assignment.session_id)
        if session is None:
            violations.append(
                ConstraintViolation(
                    code="INVALID_SESSION",
                    message=f"Assignment references unknown session '{assignment.session_id}'.",
                    severity="hard",
                )
            )
            continue

        # 2. Validate room reference
        room = rooms_by_id.get(assignment.room_id)
        if room is None:
            violations.append(
                ConstraintViolation(
                    code="INVALID_ROOM",
                    message=f"Session '{session.id}' assigned to unknown room '{assignment.room_id}'.",
                    severity="hard",
                )
            )
            continue

        # 3. Validate lecturer & group references + room capacity
        if session.lecturer_id not in lecturers_by_id:
            violations.append(
                ConstraintViolation(
                    code="INVALID_LECTURER",
                    message=f"Session '{session.id}' references unknown lecturer '{session.lecturer_id}'.",
                    severity="hard",
                )
            )

        group = groups_by_id.get(session.group_id)
        if group is None:
            violations.append(
                ConstraintViolation(
                    code="INVALID_GROUP",
                    message=f"Session '{session.id}' references unknown group '{session.group_id}'.",
                    severity="hard",
                )
            )
        elif room.capacity < group.size:
            violations.append(
                ConstraintViolation(
                    code="ROOM_CAPACITY",
                    message=(
                        f"Room '{room.id}' capacity ({room.capacity}) is smaller than "
                        f"group '{group.id}' size ({group.size}) for session '{session.id}'."
                    ),
                    severity="hard",
                )
            )
        
        # 4. Validate day & multi-slot time boundaries
        if assignment.day < 0 or assignment.day >= num_days:
            violations.append(
                ConstraintViolation(
                    code="INVALID_DAY",
                    message=f"Session '{session.id}' scheduled on invalid day index {assignment.day}.",
                    severity="hard",
                )
            )
            continue

        if (
            session.duration <= 0
            or assignment.start_slot < 0
            or assignment.start_slot + session.duration > slots_per_day
        ):
            violations.append(
                ConstraintViolation(
                    code="OUT_OF_BOUNDS",
                    message=(
                        f"Session '{session.id}' (start={assignment.start_slot}, "
                        f"duration={session.duration}) falls outside 0..{slots_per_day - 1}."
                    ),
                    severity="hard",
                )
            )
            continue
        
        

        # 5. Check clashes across every occupied slot in the session's interval
        for slot in _occupied_slots(assignment.start_slot, session.duration):
            lec_key = (session.lecturer_id, assignment.day, slot)
            if lec_key in lecturer_slots:
                violations.append(
                    ConstraintViolation(
                        code="LECTURER_CONFLICT",
                        message=(
                            f"Lecturer '{session.lecturer_id}' has a conflict on day {assignment.day}, "
                            f"slot {slot} between '{lecturer_slots[lec_key]}' and '{session.id}'."
                        ),
                        severity="hard",
                    )
                )
            else:
                lecturer_slots[lec_key] = session.id

            grp_key = (session.group_id, assignment.day, slot)
            if grp_key in group_slots:
                violations.append(
                    ConstraintViolation(
                        code="STUDENT_GROUP_CONFLICT",
                        message=(
                            f"Group '{session.group_id}' has a conflict on day {assignment.day}, "
                            f"slot {slot} between '{group_slots[grp_key]}' and '{session.id}'."
                        ),
                        severity="hard",
                    )
                )
            else:
                group_slots[grp_key] = session.id

            rm_key = (assignment.room_id, assignment.day, slot)
            if rm_key in room_slots:
                violations.append(
                    ConstraintViolation(
                        code="ROOM_CONFLICT",
                        message=(
                            f"Room '{assignment.room_id}' has a conflict on day {assignment.day}, "
                            f"slot {slot} between '{room_slots[rm_key]}' and '{session.id}'."
                        ),
                        severity="hard",
                    )
                )
            else:
                room_slots[rm_key] = session.id

    return violations