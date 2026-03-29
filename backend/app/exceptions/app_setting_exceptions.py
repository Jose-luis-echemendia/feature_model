"""
Custom exceptions for App Setting operations.
"""

from app.exceptions import NotFoundException, ConflictException


class AppSettingNotFoundException(NotFoundException):
    """App setting not found."""

    def __init__(self, key: str):
        super().__init__(detail=f"App setting '{key}' not found")


class AppSettingConflictException(ConflictException):
    """App setting conflict."""

    def __init__(self, key: str):
        super().__init__(detail=f"App setting '{key}' already exists")
