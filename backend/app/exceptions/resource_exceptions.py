"""
Custom exceptions for Resource operations.
"""

from app.exceptions import ForbiddenException, NotFoundException, BusinessLogicException


class ResourceNotFoundException(NotFoundException):
    """Resource not found."""

    def __init__(self, resource_id: str):
        super().__init__(detail=f"Resource '{resource_id}' not found")


class ResourceAccessDeniedException(ForbiddenException):
    """Access denied to resource."""

    def __init__(self, resource_id: str | None = None):
        detail = "Not enough permissions to access resource"
        if resource_id:
            detail += f" '{resource_id}'"
        super().__init__(detail=detail)


class InvalidResourceOperationException(BusinessLogicException):
    """Invalid resource operation."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid resource: {reason}")
