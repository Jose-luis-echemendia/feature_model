"""
Custom exceptions for Configuration operations.
"""

from app.exceptions import ForbiddenException, NotFoundException, BusinessLogicException


class ConfigurationNotFoundException(NotFoundException):
    """Configuration not found."""

    def __init__(self, configuration_id: str):
        super().__init__(detail=f"Configuration '{configuration_id}' not found")


class ConfigurationAccessDeniedException(ForbiddenException):
    """Access denied to configuration."""

    def __init__(self, configuration_id: str | None = None):
        detail = "Not enough permissions to access configuration"
        if configuration_id:
            detail += f" '{configuration_id}'"
        super().__init__(detail=detail)


class InvalidConfigurationOperationException(BusinessLogicException):
    """Invalid configuration operation."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid configuration: {reason}")
