"""
Custom exceptions for Tag operations.
"""

from app.exceptions import ForbiddenException, NotFoundException, ConflictException


class TagNotFoundException(NotFoundException):
    """Tag not found."""

    def __init__(self, tag_id: str):
        super().__init__(detail=f"Tag '{tag_id}' not found")


class TagAlreadyExistsException(ConflictException):
    """Tag already exists."""

    def __init__(self, tag_name: str):
        super().__init__(detail=f"Tag '{tag_name}' already exists")


class TagAccessDeniedException(ForbiddenException):
    """Access denied to tag."""

    def __init__(self, tag_id: str | None = None):
        detail = "Not enough permissions to access tag"
        if tag_id:
            detail += f" '{tag_id}'"
        super().__init__(detail=detail)
