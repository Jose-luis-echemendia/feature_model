"""
Unit tests for Domain custom exceptions.

This module tests all domain-specific exceptions to ensure they:
1. Inherit from the correct base exception class
2. Return the correct HTTP status code
3. Generate descriptive error messages
4. Include relevant context in the message
"""

import pytest
from fastapi import HTTPException

from app.exceptions import (
    # Domain entity exceptions
    DomainNotFoundException,
    DomainAlreadyExistsException,
    InvalidDomainNameException,
    # Domain operations
    DomainHasDependenciesException,
    DomainUpdateConflictException,
    # Domain state
    DomainAlreadyActiveException,
    DomainAlreadyInactiveException,
    DomainInactiveException,
    # Domain validation
    InvalidDomainDescriptionException,
    DomainAccessDeniedException,
)


# ======================================================================================
#                           Domain Entity Exceptions Tests
# ======================================================================================


class TestDomainEntityExceptions:
    """Tests for domain entity-related exceptions."""

    def test_domain_not_found_exception(self):
        """Test DomainNotFoundException with domain ID."""
        domain_id = "123e4567-e89b-12d3-a456-426614174000"
        exception = DomainNotFoundException(domain_id=domain_id)

        assert exception.status_code == 404
        assert domain_id in exception.detail
        assert "not found" in exception.detail.lower()

    def test_domain_already_exists_exception(self):
        """Test DomainAlreadyExistsException with domain name."""
        domain_name = "E-Commerce"
        exception = DomainAlreadyExistsException(domain_name=domain_name)

        assert exception.status_code == 409
        assert domain_name in exception.detail
        assert "already exists" in exception.detail.lower()

    def test_domain_already_exists_exception_with_id(self):
        """Test DomainAlreadyExistsException with domain name and existing ID."""
        domain_name = "E-Commerce"
        existing_id = "abc123"
        exception = DomainAlreadyExistsException(
            domain_name=domain_name, existing_domain_id=existing_id
        )

        assert exception.status_code == 409
        assert domain_name in exception.detail
        assert existing_id in exception.detail
        assert "already exists" in exception.detail.lower()

    def test_invalid_domain_name_exception(self):
        """Test InvalidDomainNameException with invalid name and reason."""
        domain_name = ""
        reason = "Domain name cannot be empty"
        exception = InvalidDomainNameException(domain_name=domain_name, reason=reason)

        assert exception.status_code == 422
        assert reason in exception.detail
        assert "invalid" in exception.detail.lower()


# ======================================================================================
#                           Domain Operations Exceptions Tests
# ======================================================================================


class TestDomainOperationsExceptions:
    """Tests for domain operation-related exceptions."""

    def test_domain_has_dependencies_exception(self):
        """Test DomainHasDependenciesException with feature models."""
        domain_id = "123"
        domain_name = "E-Commerce"
        dependency_count = 5

        exception = DomainHasDependenciesException(
            domain_id=domain_id,
            domain_name=domain_name,
            dependency_count=dependency_count,
            dependency_type="feature models",
        )

        assert exception.status_code == 400
        assert domain_id in exception.detail
        assert domain_name in exception.detail
        assert str(dependency_count) in exception.detail
        assert "feature models" in exception.detail
        assert "cannot delete" in exception.detail.lower()

    def test_domain_has_dependencies_exception_default_type(self):
        """Test DomainHasDependenciesException with default dependency type."""
        exception = DomainHasDependenciesException(
            domain_id="123",
            domain_name="Test Domain",
            dependency_count=3,
        )

        assert exception.status_code == 400
        assert "feature models" in exception.detail  # Default type

    def test_domain_update_conflict_exception(self):
        """Test DomainUpdateConflictException with conflicting field."""
        domain_id = "123"
        conflicting_field = "name"
        conflicting_value = "E-Commerce"

        exception = DomainUpdateConflictException(
            domain_id=domain_id,
            conflicting_field=conflicting_field,
            conflicting_value=conflicting_value,
        )

        assert exception.status_code == 409
        assert domain_id in exception.detail
        assert conflicting_field in exception.detail
        assert conflicting_value in exception.detail
        assert "cannot update" in exception.detail.lower()


# ======================================================================================
#                           Domain State Exceptions Tests
# ======================================================================================


class TestDomainStateExceptions:
    """Tests for domain state-related exceptions."""

    def test_domain_already_active_exception(self):
        """Test DomainAlreadyActiveException."""
        domain_id = "123"
        domain_name = "E-Commerce"

        exception = DomainAlreadyActiveException(
            domain_id=domain_id, domain_name=domain_name
        )

        assert exception.status_code == 400
        assert domain_id in exception.detail
        assert domain_name in exception.detail
        assert "already active" in exception.detail.lower()

    def test_domain_already_inactive_exception(self):
        """Test DomainAlreadyInactiveException."""
        domain_id = "456"
        domain_name = "Healthcare"

        exception = DomainAlreadyInactiveException(
            domain_id=domain_id, domain_name=domain_name
        )

        assert exception.status_code == 400
        assert domain_id in exception.detail
        assert domain_name in exception.detail
        assert "already inactive" in exception.detail.lower()

    def test_domain_inactive_exception(self):
        """Test DomainInactiveException with operation context."""
        domain_id = "789"
        domain_name = "Finance"
        operation = "create feature model"

        exception = DomainInactiveException(
            domain_id=domain_id, domain_name=domain_name, operation=operation
        )

        assert exception.status_code == 400
        assert domain_id in exception.detail
        assert domain_name in exception.detail
        assert operation in exception.detail
        assert "inactive" in exception.detail.lower()


# ======================================================================================
#                           Domain Validation Exceptions Tests
# ======================================================================================


class TestDomainValidationExceptions:
    """Tests for domain validation-related exceptions."""

    def test_invalid_domain_description_exception(self):
        """Test InvalidDomainDescriptionException."""
        reason = "Description exceeds maximum length of 500 characters"
        exception = InvalidDomainDescriptionException(reason=reason)

        assert exception.status_code == 422
        assert reason in exception.detail
        assert "invalid" in exception.detail.lower()
        assert "description" in exception.detail.lower()

    def test_domain_access_denied_exception(self):
        """Test DomainAccessDeniedException."""
        domain_id = "123"
        domain_name = "E-Commerce"
        user_role = "VIEWER"

        exception = DomainAccessDeniedException(
            domain_id=domain_id, domain_name=domain_name, user_role=user_role
        )

        assert exception.status_code == 400
        assert domain_id in exception.detail
        assert domain_name in exception.detail
        assert user_role in exception.detail
        assert "access denied" in exception.detail.lower()


# ======================================================================================
#                           Exception Inheritance Tests
# ======================================================================================


class TestDomainExceptionInheritance:
    """Tests to verify that all domain exceptions inherit from HTTPException."""

    def test_all_exceptions_inherit_from_http_exception(self):
        """Verify that all domain exceptions are HTTPException subclasses."""
        exceptions_to_test = [
            DomainNotFoundException("123"),
            DomainAlreadyExistsException("Test", None),
            InvalidDomainNameException("", "reason"),
            DomainHasDependenciesException("123", "Test", 5),
            DomainUpdateConflictException("123", "name", "Test"),
            DomainAlreadyActiveException("123", "Test"),
            DomainAlreadyInactiveException("123", "Test"),
            DomainInactiveException("123", "Test", "operation"),
            InvalidDomainDescriptionException("reason"),
            DomainAccessDeniedException("123", "Test", "VIEWER"),
        ]

        for exception in exceptions_to_test:
            assert isinstance(
                exception, HTTPException
            ), f"{exception.__class__.__name__} should inherit from HTTPException"


# ======================================================================================
#                           Error Message Quality Tests
# ======================================================================================


class TestDomainExceptionMessageQuality:
    """Tests to ensure error messages are descriptive and helpful."""

    def test_domain_not_found_includes_actionable_info(self):
        """Test that DomainNotFoundException includes actionable information."""
        exception = DomainNotFoundException(
            domain_id="123e4567-e89b-12d3-a456-426614174000"
        )

        # Should include the ID for debugging
        assert "123e4567-e89b-12d3-a456-426614174000" in exception.detail

    def test_domain_has_dependencies_includes_solution(self):
        """Test that DomainHasDependenciesException suggests solution."""
        exception = DomainHasDependenciesException(
            domain_id="123",
            domain_name="Test",
            dependency_count=5,
            dependency_type="feature models",
        )

        # Should suggest what to do
        detail_lower = exception.detail.lower()
        assert "delete them first" in detail_lower or "deactivate" in detail_lower

    def test_domain_inactive_exception_includes_solution(self):
        """Test that DomainInactiveException suggests activation."""
        exception = DomainInactiveException(
            domain_id="123", domain_name="Test", operation="create feature model"
        )

        # Should suggest activating the domain
        assert "activate" in exception.detail.lower()

    def test_all_exceptions_have_non_empty_messages(self):
        """Verify that all exceptions have non-empty, descriptive messages."""
        exceptions = [
            DomainNotFoundException("123"),
            DomainAlreadyExistsException("Test", None),
            InvalidDomainNameException("", "Empty name"),
            DomainHasDependenciesException("123", "Test", 5),
            DomainUpdateConflictException("123", "name", "Test"),
            DomainAlreadyActiveException("123", "Test"),
            DomainAlreadyInactiveException("123", "Test"),
            DomainInactiveException("123", "Test", "operation"),
            InvalidDomainDescriptionException("Too long"),
            DomainAccessDeniedException("123", "Test", "VIEWER"),
        ]

        for exception in exceptions:
            assert (
                exception.detail
            ), f"{exception.__class__.__name__} has empty detail message"
            assert (
                len(exception.detail) > 10
            ), f"{exception.__class__.__name__} detail message is too short"
