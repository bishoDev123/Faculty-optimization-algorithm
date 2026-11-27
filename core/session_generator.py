# Converts course requirements into individual teaching sessions
from core.models import Course, LectureSession


def generate_sessions(courses: list[Course]) -> list[LectureSession]:
    
    sessions = []
    
    # validate positive values and compaitable duration with weekly hours
    for course in courses:
        if course.duration <= 0:
            raise ValueError("Invalid duration value")
        if course.weekly_hours <= 0:
            raise ValueError("Invalid weekly hours value")
        if course.weekly_hours % course.duration != 0:
            raise ValueError(f"Invalid weekly hours with the duration of {course.id}")
        
        # define the session through the courses value
        number_of_sessions = (course.weekly_hours // course.duration)
        
        for i in range(number_of_sessions):
            session = LectureSession(
                id=f"{course.id}-S{i + 1}",
                course_id=course.id,
                lecturer_id=course.lecturer_id,
                group_id=course.group_id,
                duration=course.duration
            )
            
            sessions.append(session)
    return sessions
            