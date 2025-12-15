"""
Custom exceptions for Domain operations.

This module defines domain-specific exceptions for better error handling
and more descriptive error messages in the Domain management system.

Exception Categories:
- Domain Entity: Not found, validation errors
- Domain Operations: Create, update, delete restrictions
- Domain State: Active/inactive status issues
"""

from app.exceptions import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
    UnprocessableEntityException,
)


# ======================================================================================
#                           Domain Entity Exceptions
# ======================================================================================


class DomainNotFoundException(NotFoundException):
    """
    Exception raised when a domain is not found.

    HTTP Status: 404 Not Found

    Use when:
    - Requested domain ID doesn't exist in database
    - Domain was deleted or never existed

    Example:
        raise DomainNotFoundException(domain_id="123e4567-e89b-12d3-a456-426614174000")
    """

    def __init__(self, domain_id: str):
        super().__init__(detail=f"Domain with ID '{domain_id}' not found")


class DomainAlreadyExistsException(ConflictException):
    """
    Exception raised when attempting to create a domain with duplicate name.

    HTTP Status: 409 Conflict

    Use when:
    - Creating domain with name that already exists
    - Domain name must be unique within the system

    Example:
        raise DomainAlreadyExistsException(
            domain_name="E-Commerce",
            existing_domain_id="abc123"
        )
    """

    def __init__(self, domain_name: str, existing_domain_id: str | None = None):
        detail = f"Domain with name '{domain_name}' already exists"
        if existing_domain_id:
            detail += f" (ID: {existing_domain_id})"
        super().__init__(detail=detail)


class InvalidDomainNameException(UnprocessableEntityException):
    """
    Exception raised when domain name is invalid.

    HTTP Status: 422 Unprocessable Entity

    Use when:
    - Domain name is too short/long
    - Domain name contains invalid characters
    - Domain name doesn't meet validation rules

    Example:
        raise InvalidDomainNameException(
            domain_name="",
            reason="Domain name cannot be empty"
        )
    """

    def __init__(self, domain_name: str, reason: str):
        super().__init__(detail=f"Invalid domain name '{domain_name}': {reason}")


# ======================================================================================
#                           Domain Operations Exceptions
# ======================================================================================


class DomainHasDependenciesException(BusinessLogicException):
    """
    Exception raised when trying to delete a domain with dependencies.

    HTTP Status: 400 Bad Request

    Use when:
    - Attempting to delete domain that has feature models
    - Domain has other resources that must be deleted first

    Example:
        raise DomainHasDependenciesException(
            domain_id="123",
            domain_name="E-Commerce",
            dependency_count=5,
            dependency_type="feature models"
        )
    """

    def __init__(
        self,
        domain_id: str,
        domain_name: str,
        dependency_count: int,
        dependency_type: str = "feature models",
    ):
        super().__init__(
            detail=(
                f"Cannot delete domain '{domain_name}' (ID: {domain_id}). "
                f"It has {dependency_count} associated {dependency_type}. "
                f"Delete them first or use deactivate instead."
            )
        )


class DomainUpdateConflictException(ConflictException):
    """
    Exception raised when domain update creates a conflict.

    HTTP Status: 409 Conflict

    Use when:
    - Updating domain name to one that already exists
    - Update violates uniqueness constraints

    Example:
        raise DomainUpdateConflictException(
            domain_id="123",
            conflicting_field="name",
            conflicting_value="E-Commerce"
        )
    """

    def __init__(self, domain_id: str, conflicting_field: str, conflicting_value: str):
        super().__init__(
            detail=(
                f"Cannot update domain {domain_id}: "
                f"{conflicting_field} '{conflicting_value}' already exists"
            )
        )


# ======================================================================================
#                           Domain State Exceptions
# ======================================================================================


class DomainAlreadyActiveException(BusinessLogicException):
    """
    Exception raised when trying to activate an already active domain.

    HTTP Status: 400 Bad Request

    Use when:
    - Attempting to activate a domain that is already active
    - Operation is redundant

    Example:
        raise DomainAlreadyActiveException(
            domain_id="123",
            domain_name="E-Commerce"
        )
    """

    def __init__(self, domain_id: str, domain_name: str):
        super().__init__(
            detail=f"Domain '{domain_name}' (ID: {domain_id}) is already active"
        )


class DomainAlreadyInactiveException(BusinessLogicException):
    """
    Exception raised when trying to deactivate an already inactive domain.

    HTTP Status: 400 Bad Request

    Use when:
    - Attempting to deactivate a domain that is already inactive
    - Operation is redundant

    Example:
        raise DomainAlreadyInactiveException(
            domain_id="123",
            domain_name="E-Commerce"
        )
    """

    def __init__(self, domain_id: str, domain_name: str):
        super().__init__(
            detail=f"Domain '{domain_name}' (ID: {domain_id}) is already inactive"
        )


class DomainInactiveException(BusinessLogicException):
    """
    Exception raised when trying to use an inactive domain.

    HTTP Status: 400 Bad Request

    Use when:
    - Attempting to create feature models in inactive domain
    - Attempting operations that require active domain

    Example:
        raise DomainInactiveException(
            domain_id="123",
            domain_name="E-Commerce",
            operation="create feature model"
        )
    """

    def __init__(self, domain_id: str, domain_name: str, operation: str):
        super().__init__(
            detail=(
                f"Cannot {operation}: Domain '{domain_name}' (ID: {domain_id}) "
                f"is inactive. Activate it first."
            )
        )


# ======================================================================================
#                           Domain Validation Exceptions
# ======================================================================================


class InvalidDomainDescriptionException(UnprocessableEntityException):
    """
    Exception raised when domain description is invalid.

    HTTP Status: 422 Unprocessable Entity

    Use when:
    - Description is too long
    - Description contains invalid content

    Example:
        raise InvalidDomainDescriptionException(
            reason="Description exceeds maximum length of 500 characters"
        )
    """

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid domain description: {reason}")


class DomainAccessDeniedException(BusinessLogicException):
    """
    Exception raised when user doesn't have access to domain.

    HTTP Status: 403 Forbidden

    Use when:
    - User tries to access domain they don't have permissions for
    - Domain is restricted to certain roles

    Example:
        raise DomainAccessDeniedException(
            domain_id="123",
            domain_name="E-Commerce",
            user_role="VIEWER"
        )
    """

    def __init__(self, domain_id: str, domain_name: str, user_role: str):
        super().__init__(
            detail=(
                f"Access denied to domain '{domain_name}' (ID: {domain_id}). "
                f"Role '{user_role}' does not have sufficient permissions."
            )
        )
