# 	Defines the common result returned by both algorithms

from dataclasses import dataclass

@dataclass
class OptimizationResult:
    pass

@dataclass
class ValidationResult:
    pass

@dataclass
class ConstraintViolation:
    pass
