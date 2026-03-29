"""
Custom exceptions for User operations.
"""

from app.exceptions import ForbiddenException, NotFoundException, ConflictException


class UserNotFoundException(NotFoundException):
    """User not found."""

    def __init__(self, user_id: str):
        super().__init__(detail=f"User '{user_id}' not found")


class UserAlreadyExistsException(ConflictException):
    """User already exists."""

    def __init__(self, email: str):
        super().__init__(detail=f"User with email '{email}' already exists")


class UserAccessDeniedException(ForbiddenException):
    """Access denied to user."""

    def __init__(self, user_id: str | None = None):
        detail = "Not enough permissions to access user"
        if user_id:
            detail += f" '{user_id}'"
        super().__init__(detail=detail)
