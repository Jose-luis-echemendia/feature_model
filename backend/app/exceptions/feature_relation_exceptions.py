"""
Custom exceptions for Feature Relation operations.
"""

from app.exceptions import ForbiddenException, NotFoundException, BusinessLogicException


class FeatureRelationNotFoundException(NotFoundException):
    """Feature relation not found."""

    def __init__(self, relation_id: str):
        super().__init__(detail=f"Feature relation '{relation_id}' not found")


class FeatureRelationAccessDeniedException(ForbiddenException):
    """Access denied to feature relation."""

    def __init__(self, relation_id: str | None = None):
        detail = "Not enough permissions to access feature relation"
        if relation_id:
            detail += f" '{relation_id}'"
        super().__init__(detail=detail)


class InvalidFeatureRelationException(BusinessLogicException):
    """Invalid feature relation operation."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid feature relation: {reason}")
