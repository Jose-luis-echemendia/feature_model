from fastapi import HTTPException

from app.exceptions import (
    AppSettingConflictException,
    AppSettingNotFoundException,
    ConfigurationAccessDeniedException,
    ConfigurationNotFoundException,
    ConstraintAccessDeniedException,
    ConstraintNotFoundException,
    FeatureAccessDeniedException,
    FeatureAlreadyExistsException,
    FeatureGroupAccessDeniedException,
    FeatureGroupNotFoundException,
    FeatureRelationAccessDeniedException,
    FeatureRelationNotFoundException,
    InvalidConfigurationOperationException,
    InvalidConstraintOperationException,
    InvalidFeatureGroupException,
    InvalidFeatureRelationException,
    InvalidResourceOperationException,
    ResourceAccessDeniedException,
    ResourceNotFoundException,
    TagAccessDeniedException,
    TagAlreadyExistsException,
    TagNotFoundException,
    UserAccessDeniedException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


def _assert_http_exception(
    exc: HTTPException, expected_status: int, *expected_fragments: str
) -> None:
    assert isinstance(exc, HTTPException)
    assert exc.status_code == expected_status
    detail = str(exc.detail).lower()
    for fragment in expected_fragments:
        assert fragment.lower() in detail


def test_additional_exceptions_status_codes_and_messages() -> None:
    cases = [
        (AppSettingNotFoundException("k1"), 404, "k1"),
        (AppSettingConflictException("k1"), 409, "already exists"),
        (ConfigurationNotFoundException("cfg1"), 404, "cfg1"),
        (ConfigurationAccessDeniedException("cfg1"), 403, "permissions", "cfg1"),
        (ConfigurationAccessDeniedException(), 403, "permissions", "configuration"),
        (
            InvalidConfigurationOperationException("bad config"),
            400,
            "bad config",
        ),
        (ConstraintNotFoundException("ct1"), 404, "ct1"),
        (ConstraintAccessDeniedException("ct1"), 403, "permissions", "ct1"),
        (ConstraintAccessDeniedException(), 403, "permissions", "constraint"),
        (InvalidConstraintOperationException("bad constraint"), 400, "bad constraint"),
        (FeatureAccessDeniedException("f1"), 403, "permissions", "f1"),
        (FeatureAccessDeniedException(), 403, "permissions", "feature"),
        (FeatureAlreadyExistsException("Root"), 409, "root"),
        (FeatureGroupNotFoundException("g1"), 404, "g1"),
        (FeatureGroupAccessDeniedException("g1"), 403, "permissions", "g1"),
        (
            InvalidFeatureGroupException("invalid cardinality"),
            400,
            "invalid cardinality",
        ),
        (FeatureRelationNotFoundException("r1"), 404, "r1"),
        (FeatureRelationAccessDeniedException("r1"), 403, "permissions", "r1"),
        (FeatureRelationAccessDeniedException(), 403, "permissions", "relation"),
        (InvalidFeatureRelationException("invalid relation"), 400, "invalid relation"),
        (ResourceNotFoundException("res1"), 404, "res1"),
        (ResourceAccessDeniedException("res1"), 403, "permissions", "res1"),
        (ResourceAccessDeniedException(), 403, "permissions", "resource"),
        (
            InvalidResourceOperationException("invalid resource"),
            400,
            "invalid resource",
        ),
        (TagNotFoundException("t1"), 404, "t1"),
        (TagAlreadyExistsException("backend"), 409, "backend"),
        (TagAccessDeniedException("t1"), 403, "permissions", "t1"),
        (TagAccessDeniedException(), 403, "permissions", "tag"),
        (UserNotFoundException("u1"), 404, "u1"),
        (UserAlreadyExistsException("mail@example.com"), 409, "mail@example.com"),
        (UserAccessDeniedException("u1"), 403, "permissions", "u1"),
        (UserAccessDeniedException(), 403, "permissions", "user"),
    ]

    for exc, status, *fragments in cases:
        _assert_http_exception(exc, status, *fragments)
