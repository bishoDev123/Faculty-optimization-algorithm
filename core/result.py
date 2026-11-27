# 	Defines the common result returned by both algorithms
from dataclasses import dataclass
from core.models import Timetable

@dataclass
class ConstraintViolation:
    code: str
    message: str
    severity: str
    
@dataclass
class OptimizationResult:
    algorithm: str
    best_timetable: Timetable
    best_fitness: float
    hard_violations: list[ConstraintViolation]
    execution_time: float
    fitness_history: list[float]
    generations: int
    validation: ValidationResult
    metadata: dict
@dataclass
class ValidationResult:
    is_valid: bool
    hard_violations: list[ConstraintViolation]
    missing_session_ids: list[str]
    duplicate_session_ids: list[str]
