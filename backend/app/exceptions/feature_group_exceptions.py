"""
Custom exceptions for Feature Group operations.
"""

from app.exceptions import BusinessLogicException, ForbiddenException, NotFoundException


class FeatureGroupNotFoundException(NotFoundException):
    """Feature group not found."""

    def __init__(self, group_id: str):
        super().__init__(detail=f"Feature group '{group_id}' not found")


class FeatureGroupAccessDeniedException(ForbiddenException):
    """Access denied to feature group."""

    def __init__(self, group_id: str):
        super().__init__(
            detail=f"Not enough permissions to access feature group '{group_id}'"
        )


class InvalidFeatureGroupException(BusinessLogicException):
    """Invalid feature group operation."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid feature group: {reason}")
