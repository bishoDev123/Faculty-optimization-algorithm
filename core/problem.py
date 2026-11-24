# Validate the input data required for timetable optimization.

#     Checks:
#         - Unique entity IDs
#         - Valid lecturer and group references
#         - Valid room and group capacities
#         - Valid course requirements
#         - Valid timetable configuration
#         - Generated session consistency

#     Returns:
#         ValidationResult containing all detected violations.

from core.models import Problem
from core.result import ValidationResult, ConstraintViolation


def validate_problem_data(problem: Problem) -> ValidationResult:

    violations = []

    entities = {
        "lecturer": problem.lecturers,
        "group": problem.groups,
        "room": problem.rooms,
        "course": problem.courses,
        "session": problem.sessions
    }

    # Validate unique IDs using sets
    for entity_type, items in entities.items():
        seen_ids = set()

        for item in items:
            if item.id in seen_ids:
                violations.append(
                    ConstraintViolation(
                        code="DUPLICATE_ID",
                        message=(
                            f"Duplicate {entity_type} ID: {item.id}"
                        ),
                        severity="hard"
                    )
                )
            else:
                seen_ids.add(item.id)


    # Validate lecturer references
    lecturer_ids = {lecturer.id for lecturer in problem.lecturers}

    for course in problem.courses:
        if course.lecturer_id not in lecturer_ids:
            violations.append(
                ConstraintViolation(
                    code="INVALID_LECTURER_REFERENCE",
                    message=(
                        f"Course {course.id} references "
                        f"nonexistent lecturer {course.lecturer_id}"
                    ),
                    severity="hard"
                )
            )

    # Validate student group references
    group_ids = {group.id for group in problem.groups}

    for course in problem.courses:
        if course.group_id not in group_ids:
            violations.append(
                ConstraintViolation(
                    code="INVALID_GROUP_REFERENCE",
                    message=(
                        f"Course {course.id} references "
                        f"nonexistent group {course.group_id}"
                    ),
                    severity="hard"
                )
            )

    # 4. Validate room capacities
    for room in problem.rooms:
        if room.capacity <= 0:
            violations.append(
                ConstraintViolation(
                    code="INVALID_ROOM_CAPACITY",
                    message=(
                        f"Room {room.id} has invalid capacity "
                        f"{room.capacity}"
                    ),
                    severity="hard"
                )
            )

    # 5. Validate student group sizes not negative
    for group in problem.groups:
        if group.size <= 0:
            violations.append(
                ConstraintViolation(
                    code="INVALID_GROUP_SIZE",
                    message=(
                        f"Group {group.id} has invalid size {group.size}"
                    ),
                    severity="hard"
                )
            )

    # Validate course requirements not negative and compaitable
    for course in problem.courses:

        if course.weekly_hours <= 0:
            violations.append(
                ConstraintViolation(
                    code="INVALID_WEEKLY_HOURS",
                    message=(
                        f"Course {course.id} has invalid "
                        f"weekly hours: {course.weekly_hours}"
                    ),
                    severity="hard"
                )
            )

        if course.duration <= 0:
            violations.append(
                ConstraintViolation(
                    code="INVALID_COURSE_DURATION",
                    message=(
                        f"Course {course.id} has invalid "
                        f"duration: {course.duration}"
                    ),
                    severity="hard"
                )
            )

        elif (
            course.weekly_hours > 0
            and course.weekly_hours % course.duration != 0
        ):
            violations.append(
                ConstraintViolation(
                    code="INCOMPATIBLE_COURSE_DURATION",
                    message=(
                        f"Course {course.id}: weekly hours "
                        f"({course.weekly_hours}) are not divisible "
                        f"by duration ({course.duration})"
                    ),
                    severity="hard"
                )
            )

    # Validate timetable configuration
    
    # no days
    if not problem.days:
        violations.append(
            ConstraintViolation(
                code="NO_AVAILABLE_DAYS",
                message="The timetable has no available days",
                severity="hard"
            )
        )

    # duplicate days
    if len(problem.days) != len(set(problem.days)):
        violations.append(
            ConstraintViolation(
                code="DUPLICATE_DAYS",
                message="The timetable contains duplicate days",
                severity="hard"
            )
        )

    # negative slots per day
    if problem.slots_per_day <= 0:
        violations.append(
            ConstraintViolation(
                code="INVALID_SLOTS_PER_DAY",
                message=(
                    f"Invalid number of slots per day: "
                    f"{problem.slots_per_day}"
                ),
                severity="hard"
            )
        )

    # Validate generated sessions
    course_map = {
        course.id: course
        for course in problem.courses
    }

    session_ids_by_course = {
        course.id: []
        for course in problem.courses
    }

    for session in problem.sessions:

        course = course_map.get(session.course_id)

        # Checks if the course is in the map
        if course is None:
            violations.append(
                ConstraintViolation(
                    code="INVALID_SESSION_COURSE",
                    message=(
                        f"Session {session.id} references "
                        f"nonexistent course {session.course_id}"
                    ),
                    severity="hard"
                )
            )
            continue

        session_ids_by_course[course.id].append(session.id)

        # Checks if the mapped lecturer isn't the same as in the session
        if session.lecturer_id != course.lecturer_id:
            violations.append(
                ConstraintViolation(
                    code="SESSION_LECTURER_MISMATCH",
                    message=(
                        f"Session {session.id} has a lecturer "
                        f"different from course {course.id}"
                    ),
                    severity="hard"
                )
            )
            
        # Checks if the mapped student group isn't the same as in the session
        if session.group_id != course.group_id:
            violations.append(
                ConstraintViolation(
                    code="SESSION_GROUP_MISMATCH",
                    message=(
                        f"Session {session.id} has a group "
                        f"different from course {course.id}"
                    ),
                    severity="hard"
                )
            )

        # Checks if the mapped course duration isn't the same as in the session
        if session.duration != course.duration:
            violations.append(
                ConstraintViolation(
                    code="SESSION_DURATION_MISMATCH",
                    message=(
                        f"Session {session.id} has an incorrect duration"
                    ),
                    severity="hard"
                )
            )

        # checks if the session has a negative duration
        if session.duration <= 0:
            violations.append(
                ConstraintViolation(
                    code="INVALID_SESSION_DURATION",
                    message=(
                        f"Session {session.id} has invalid duration "
                        f"{session.duration}"
                    ),
                    severity="hard"
                )
            )

    # Check expected session counts
    for course in problem.courses:

        if course.duration <= 0 or course.weekly_hours <= 0:
            continue

        if course.weekly_hours % course.duration != 0:
            continue

        expected_count = (
            course.weekly_hours // course.duration
        )

        actual_count = len(session_ids_by_course[course.id])

        if actual_count != expected_count:
            violations.append(
                ConstraintViolation(
                    code="INCORRECT_SESSION_COUNT",
                    message=(
                        f"Course {course.id} requires "
                        f"{expected_count} sessions but has "
                        f"{actual_count}"
                    ),
                    severity="hard"
                )
            )

    # Build validation result
    return ValidationResult(
        is_valid=len(violations) == 0,
        hard_violations=violations,
        missing_session_ids=[],
        duplicate_session_ids=[]
    )
