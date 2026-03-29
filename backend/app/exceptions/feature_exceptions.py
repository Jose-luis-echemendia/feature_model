"""
Custom exceptions for Feature operations.
"""

from app.exceptions import ForbiddenException, ConflictException


class FeatureAccessDeniedException(ForbiddenException):
    """Access denied to feature."""

    def __init__(self, feature_id: str | None = None):
        detail = "Not enough permissions to access feature"
        if feature_id:
            detail += f" '{feature_id}'"
        super().__init__(detail=detail)


class FeatureAlreadyExistsException(ConflictException):
    """Feature already exists."""

    def __init__(self, feature_name: str):
        super().__init__(detail=f"Feature '{feature_name}' already exists")
