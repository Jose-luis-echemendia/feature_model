"""
Custom exceptions for Constraint operations.
"""

from app.exceptions import ForbiddenException, NotFoundException, BusinessLogicException


class ConstraintNotFoundException(NotFoundException):
    """Constraint not found."""

    def __init__(self, constraint_id: str):
        super().__init__(detail=f"Constraint '{constraint_id}' not found")


class ConstraintAccessDeniedException(ForbiddenException):
    """Access denied to constraint."""

    def __init__(self, constraint_id: str | None = None):
        detail = "Not enough permissions to access constraint"
        if constraint_id:
            detail += f" '{constraint_id}'"
        super().__init__(detail=detail)


class InvalidConstraintOperationException(BusinessLogicException):
    """Invalid constraint operation."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid constraint: {reason}")
