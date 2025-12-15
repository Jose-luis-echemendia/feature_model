"""
Excepciones de la aplicación.

Este módulo centraliza todas las excepciones personalizadas de la aplicación,
tanto las genéricas como las específicas del dominio de Feature Models.
"""

from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from .exceptions import (
    NotFoundException,
    BusinessLogicException,
    UnprocessableEntityException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)

from .feature_model_exceptions import (
    # Feature Model base exceptions
    FeatureModelNotFoundException,
    FeatureModelVersionNotFoundException,
    FeatureNotFoundException,
    # Version management
    InvalidVersionStateException,
    VersionAlreadyPublishedException,
    NoPublishedVersionException,
    # Structural validation
    InvalidTreeStructureException,
    MissingRootFeatureException,
    MultipleRootFeaturesException,
    CyclicDependencyException,
    OrphanFeatureException,
    # Relationship validation
    InvalidRelationException,
    SelfRelationException,
    DuplicateRelationException,
    ConflictingRelationsException,
    # Group validation
    InvalidGroupCardinalityException,
    EmptyGroupException,
    InvalidAlternativeGroupException,
    InvalidOrGroupException,
    # Constraint validation
    InvalidConstraintException,
    UnsatisfiableConstraintException,
    ConflictingConstraintsException,
    # Configuration validation
    InvalidConfigurationException,
    MandatoryFeatureMissingException,
    ExcludedFeaturesSelectedException,
    RequiredFeatureMissingException,
    GroupCardinalityViolationException,
    # Export
    UnsupportedExportFormatException,
    ExportFailedException,
    # Analysis
    DeadFeatureDetectedException,
    FalseOptionalDetectedException,
)

from .domain_exceptions import (
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

__all__ = [
    # FastAPI exceptions
    "RequestValidationError",
    "HTTPException",
    # Exception handlers
    "validation_exception_handler",
    "http_exception_handler",
    "generic_exception_handler",
    # Generic exceptions
    "NotFoundException",
    "BusinessLogicException",
    "UnprocessableEntityException",
    "ConflictException",
    "ForbiddenException",
    "UnauthorizedException",
    # Feature Model exceptions
    "FeatureModelNotFoundException",
    "FeatureModelVersionNotFoundException",
    "FeatureNotFoundException",
    "InvalidVersionStateException",
    "VersionAlreadyPublishedException",
    "NoPublishedVersionException",
    "InvalidTreeStructureException",
    "MissingRootFeatureException",
    "MultipleRootFeaturesException",
    "CyclicDependencyException",
    "OrphanFeatureException",
    "InvalidRelationException",
    "SelfRelationException",
    "DuplicateRelationException",
    "ConflictingRelationsException",
    "InvalidGroupCardinalityException",
    "EmptyGroupException",
    "InvalidAlternativeGroupException",
    "InvalidOrGroupException",
    "InvalidConstraintException",
    "UnsatisfiableConstraintException",
    "ConflictingConstraintsException",
    "InvalidConfigurationException",
    "MandatoryFeatureMissingException",
    "ExcludedFeaturesSelectedException",
    "RequiredFeatureMissingException",
    "GroupCardinalityViolationException",
    "UnsupportedExportFormatException",
    "ExportFailedException",
    "DeadFeatureDetectedException",
    "FalseOptionalDetectedException",
    # Domain exceptions
    "DomainNotFoundException",
    "DomainAlreadyExistsException",
    "InvalidDomainNameException",
    "DomainHasDependenciesException",
    "DomainUpdateConflictException",
    "DomainAlreadyActiveException",
    "DomainAlreadyInactiveException",
    "DomainInactiveException",
    "InvalidDomainDescriptionException",
    "DomainAccessDeniedException",
]
