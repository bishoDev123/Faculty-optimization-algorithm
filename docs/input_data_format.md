# Input JSON Format

## 1. Overview

The faculty timetable optimization system receives its scheduling data through a JSON file.

The JSON file describes the faculty's:

- Lecturers
- Student groups
- Rooms
- Courses
- Available scheduling days
- Number of available time slots per day

The dataset is loaded using `load_problem()` from `data/datasets.py`.

The loader converts the JSON data into Python dataclass objects and automatically generates the required lecture sessions from the course information.

## 2. JSON Structure

A valid input JSON file follows this general structure:

```json
{
    "days": [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday"
    ],
    "slots_per_day": 6,

    "lecturers": [
        {
            "id": "L1",
            "name": "Ahmed Hassan"
        }
    ],

    "groups": [
        {
            "id": "G1",
            "name": "CS-Year-1",
            "size": 45
        }
    ],

    "rooms": [
        {
            "id": "R1",
            "name": "Lecture Hall 1",
            "capacity": 60
        }
    ],

    "courses": [
        {
            "id": "C1",
            "name": "Mathematics",
            "lecturer_id": "L1",
            "group_id": "G1",
            "weekly_hours": 3,
            "duration": 1
        }
    ]
}
```

The root JSON object must contain all six required keys:

| Key | Data type | Description |
|---|---|---|
| `days` | Array of strings | Days available for scheduling. |
| `slots_per_day` | Integer | Number of available time slots per day. |
| `lecturers` | Array of objects | Lecturers participating in the scheduling process. |
| `groups` | Array of objects | Student groups that attend courses. |
| `rooms` | Array of objects | Available classrooms and laboratories. |
| `courses` | Array of objects | Courses and their scheduling requirements. |

## 3. Entity Definitions

### 3.1 Lecturers

Each lecturer represents a faculty member who teaches one or more courses.

| Field | Data type | Description |
|---|---|---|
| `id` | String | Unique lecturer identifier. |
| `name` | String | Lecturer's name. |

Example:

```json
{
    "id": "L1",
    "name": "Ahmed Hassan"
}
```

The lecturer ID is referenced by courses through `lecturer_id`.

### 3.2 Student Groups

Each group represents a collection of students attending the same set of courses.

| Field | Data type | Description |
|---|---|---|
| `id` | String | Unique group identifier. |
| `name` | String | Group name. |
| `size` | Integer | Number of students in the group. |

Example:

```json
{
    "id": "G1",
    "name": "CS-Year-1",
    "size": 45
}
```

The group ID is referenced by courses through `group_id`.

The group size is used when checking whether an assigned room has sufficient capacity.

### 3.3 Rooms

Each room represents a classroom or laboratory available for scheduling.

| Field | Data type | Description |
|---|---|---|
| `id` | String | Unique room identifier. |
| `name` | String | Room name. |
| `capacity` | Integer | Maximum number of students the room can accommodate. |

Example:

```json
{
    "id": "R1",
    "name": "Lecture Hall 1",
    "capacity": 60
}
```

A room's capacity must be positive. During timetable validation, its capacity is compared against the size of the assigned student group.

### 3.4 Courses

Each course describes the weekly teaching requirements that must be satisfied by the timetable.

| Field | Data type | Description |
|---|---|---|
| `id` | String | Unique course identifier. |
| `name` | String | Course name. |
| `lecturer_id` | String | ID of the lecturer responsible for the course. |
| `group_id` | String | ID of the student group attending the course. |
| `weekly_hours` | Integer | Total number of timetable slots required by the course per week. |
| `duration` | Integer | Number of consecutive timetable slots occupied by each lecture session. |

Example:

```json
{
    "id": "C1",
    "name": "Mathematics",
    "lecturer_id": "L1",
    "group_id": "G1",
    "weekly_hours": 3,
    "duration": 1
}
```

The relationship between `weekly_hours` and `duration` determines how many individual lecture sessions must be generated.

This is explained in Section 4.

## 4. Understanding `weekly_hours` and `duration`

These two fields determine how a course's weekly teaching requirements are divided into individual lecture sessions.

**Important:** In the current implementation, `weekly_hours` and `duration` are measured in timetable slots, not necessarily clock hours.

### 4.1 `weekly_hours`

`weekly_hours` represents the total number of timetable slots a course must occupy during the entire week.

For example:

```json
"weekly_hours": 4
```

This means that the course requires a total of four timetable slots per week.

It does not necessarily mean four separate lecture sessions.

### 4.2 `duration`

`duration` represents the number of consecutive timetable slots occupied by one lecture session.

For example:

```json
"duration": 2
```

This means that each lecture session occupies two consecutive slots.

The duration applies to every session generated for that course.

### 4.3 Calculating the Number of Sessions

The number of sessions generated for a course is calculated using:

```python
number_of_sessions = weekly_hours // duration
```

For this calculation to produce a valid schedule, `weekly_hours` must be positive, `duration` must be positive, and `weekly_hours` must be divisible by `duration`.

Mathematically:

\[
\text{Number of Sessions} =
\frac{\text{weekly\_hours}}{\text{duration}}
\]

### 4.4 Examples

**Example 1: Three separate one-slot sessions**

```json
{
    "weekly_hours": 3,
    "duration": 1
}
```

Calculation:

\[
3 \div 1 = 3
\]

Result:

- 3 lecture sessions.
- Each session occupies 1 consecutive slot.
- Total weekly occupancy: 3 slots.

Generated sessions:

```text
C1-S1: 1 slot
C1-S2: 1 slot
C1-S3: 1 slot
```

**Example 2: Two separate two-slot sessions**

```json
{
    "weekly_hours": 4,
    "duration": 2
}
```

Calculation:

\[
4 \div 2 = 2
\]

Result:

- 2 lecture sessions.
- Each session occupies 2 consecutive slots.
- Total weekly occupancy: 4 slots.

Generated sessions:

```text
C2-S1: 2 consecutive slots
C2-S2: 2 consecutive slots
```

**Example 3: One three-slot session**

```json
{
    "weekly_hours": 3,
    "duration": 3
}
```

Calculation:

\[
3 \div 3 = 1
\]

Result:

- 1 lecture session.
- The session occupies 3 consecutive slots.
- Total weekly occupancy: 3 slots.

### 4.5 Invalid Configurations

A course is invalid if its weekly hours or duration are not positive, or if its weekly hours cannot be divided evenly by its duration.

For example:

```json
{
    "weekly_hours": 5,
    "duration": 2
}
```

Calculation:

\[
5 \div 2 = 2.5
\]

This configuration is invalid because it would require a fractional number of lecture sessions.

The system rejects this configuration rather than generating an incomplete session.

The following configurations are also invalid:

| `weekly_hours` | `duration` | Reason |
|---:|---:|---|
| 0 | 1 | Weekly hours must be positive. |
| 4 | 0 | Duration must be positive. |
| -2 | 1 | Weekly hours cannot be negative. |
| 3 | -1 | Duration cannot be negative. |
| 5 | 2 | Weekly hours must be divisible by duration. |

## 5. Scheduling Configuration

### 5.1 Days

The `days` field contains the days available for scheduling.

Example:

```json
"days": [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday"
]
```

Each day is represented by its position in the list when timetable assignments use integer day indices.

For example:

| Index | Day |
|---:|---|
| 0 | Sunday |
| 1 | Monday |
| 2 | Tuesday |
| 3 | Wednesday |
| 4 | Thursday |

The list must not be empty or contain duplicate days.

### 5.2 Slots per Day

The `slots_per_day` field defines the number of available timetable slots on each scheduling day.

Example:

```json
"slots_per_day": 6
```

With five available days and six slots per day:

\[
5 \times 6 = 30
\]

The timetable therefore has 30 available time positions per room during the week.

A session's duration determines how many consecutive positions it occupies.

## 6. Automatic Session Generation

The JSON input does not contain a separate `sessions` array.

Instead, sessions are generated automatically from the `courses` array using:

```python
generate_sessions(courses)
```

Each generated session receives:

- A unique session ID.
- Its associated course ID.
- Its lecturer ID.
- Its student group ID.
- Its duration.

For example, a course with:

```json
{
    "id": "C1",
    "name": "Programming",
    "lecturer_id": "L1",
    "group_id": "G1",
    "weekly_hours": 4,
    "duration": 2
}
```

Produces:

```text
C1-S1
C1-S2
```

Both sessions inherit the lecturer, group, and duration from the original course.

This means that the dataset only needs to describe each course once.

## 7. Input Validation Rules

The dataset must satisfy the following basic requirements:

1. The JSON file must contain a valid JSON object at its root.
2. All six required keys must be present.
3. Entity IDs must be unique within their respective entity types.
4. Course lecturer references must point to existing lecturers.
5. Course group references must point to existing student groups.
6. Room capacities must be positive.
7. Student group sizes must be positive.
8. Course weekly hours must be positive.
9. Course durations must be positive.
10. Course weekly hours must be divisible by course duration.
11. The days list must not be empty or contain duplicates.
12. The number of slots per day must be positive.
13. Generated sessions must reference valid courses and match their associated course information.
14. The number of generated sessions must match each course's required session count.

The loader validates the constructed problem before returning it.

## 8. Loading a Dataset

To load a dataset:

```python
from data.datasets import load_problem

problem = load_problem("data/raw/input_example.json")
```

The returned object is a `Problem` instance containing:

- Lecturers
- Student groups
- Rooms
- Courses
- Automatically generated sessions
- Available days
- Slots per day

This `Problem` object is the common input used by the Genetic Algorithm and Memetic Algorithm.

## 9. Adding a New Dataset

To create another dataset:

1. Create a new JSON file inside `data/raw/`.
2. Follow the structure documented in this file.
3. Assign unique IDs to all entities of the same type.
4. Make sure every course references an existing lecturer and group.
5. Verify that `weekly_hours` is divisible by `duration`.
6. Load the file using `load_problem()` to trigger structural and problem validation.

Example:

```text
data/
├── datasets.py
└── raw/
    ├── input_example.json
    ├── input_small.json
    └── input_large.json
```

Different datasets can then be used to test and benchmark the optimization algorithms against different scheduling scenarios.