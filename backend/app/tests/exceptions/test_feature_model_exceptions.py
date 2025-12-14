"""
Tests unitarios para las excepciones personalizadas de Feature Models.

Verifica que cada excepción:
- Retorne el código HTTP correcto
- Tenga mensajes descriptivos
- Se pueda instanciar correctamente
"""

import pytest
from fastapi import HTTPException

from app.exceptions import (
    # Excepciones base
    NotFoundException,
    BusinessLogicException,
    UnprocessableEntityException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
    # Feature Model
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


class TestBaseExceptions:
    """Tests para excepciones base."""

    def test_not_found_exception(self):
        """Test NotFoundException retorna 404."""
        exc = NotFoundException(detail="Test not found")
        assert exc.status_code == 404
        assert "Test not found" in str(exc.detail)

    def test_business_logic_exception(self):
        """Test BusinessLogicException retorna 400."""
        exc = BusinessLogicException(detail="Business logic error")
        assert exc.status_code == 400
        assert "Business logic error" in str(exc.detail)

    def test_unprocessable_entity_exception(self):
        """Test UnprocessableEntityException retorna 422."""
        exc = UnprocessableEntityException(detail="Invalid entity")
        assert exc.status_code == 422
        assert "Invalid entity" in str(exc.detail)

    def test_conflict_exception(self):
        """Test ConflictException retorna 409."""
        exc = ConflictException(detail="Resource conflict")
        assert exc.status_code == 409
        assert "Resource conflict" in str(exc.detail)

    def test_forbidden_exception(self):
        """Test ForbiddenException retorna 403."""
        exc = ForbiddenException(detail="Access forbidden")
        assert exc.status_code == 403
        assert "Access forbidden" in str(exc.detail)

    def test_unauthorized_exception(self):
        """Test UnauthorizedException retorna 401."""
        exc = UnauthorizedException(detail="Unauthorized")
        assert exc.status_code == 401
        assert "Unauthorized" in str(exc.detail)


class TestFeatureModelExceptions:
    """Tests para excepciones de Feature Model."""

    def test_feature_model_not_found(self):
        """Test FeatureModelNotFoundException."""
        model_id = "test-model-id"
        exc = FeatureModelNotFoundException(model_id=model_id)
        assert exc.status_code == 404
        assert model_id in str(exc.detail)

    def test_feature_model_version_not_found_with_id(self):
        """Test FeatureModelVersionNotFoundException con version_id."""
        version_id = "test-version-id"
        exc = FeatureModelVersionNotFoundException(version_id=version_id)
        assert exc.status_code == 404
        assert version_id in str(exc.detail)

    def test_feature_model_version_not_found_with_number(self):
        """Test FeatureModelVersionNotFoundException con version_number."""
        version_number = 5
        exc = FeatureModelVersionNotFoundException(version_number=version_number)
        assert exc.status_code == 404
        assert str(version_number) in str(exc.detail)

    def test_feature_not_found(self):
        """Test FeatureNotFoundException."""
        feature_id = "test-feature-id"
        exc = FeatureNotFoundException(feature_id=feature_id)
        assert exc.status_code == 404
        assert feature_id in str(exc.detail)


class TestVersionManagementExceptions:
    """Tests para excepciones de gestión de versiones."""

    def test_invalid_version_state(self):
        """Test InvalidVersionStateException."""
        exc = InvalidVersionStateException(
            current_state="PUBLISHED",
            required_state="DRAFT",
            operation="modify version",
        )
        assert exc.status_code == 400
        assert "PUBLISHED" in str(exc.detail)
        assert "DRAFT" in str(exc.detail)
        assert "modify version" in str(exc.detail)

    def test_version_already_published(self):
        """Test VersionAlreadyPublishedException."""
        version_id = "test-version-id"
        exc = VersionAlreadyPublishedException(version_id=version_id)
        assert exc.status_code == 409
        assert version_id in str(exc.detail)
        assert "immutable" in str(exc.detail).lower()

    def test_no_published_version(self):
        """Test NoPublishedVersionException."""
        model_id = "test-model-id"
        exc = NoPublishedVersionException(model_id=model_id)
        assert exc.status_code == 404
        assert model_id in str(exc.detail)


class TestStructuralValidationExceptions:
    """Tests para excepciones de validación estructural."""

    def test_invalid_tree_structure(self):
        """Test InvalidTreeStructureException."""
        reason = "Circular reference detected"
        exc = InvalidTreeStructureException(reason=reason)
        assert exc.status_code == 422
        assert reason in str(exc.detail)

    def test_missing_root_feature(self):
        """Test MissingRootFeatureException."""
        exc = MissingRootFeatureException()
        assert exc.status_code == 422
        assert "root" in str(exc.detail).lower()

    def test_multiple_root_features(self):
        """Test MultipleRootFeaturesException."""
        count = 3
        exc = MultipleRootFeaturesException(count=count)
        assert exc.status_code == 422
        assert str(count) in str(exc.detail)

    def test_cyclic_dependency(self):
        """Test CyclicDependencyException."""
        cycle_description = "A -> B -> C -> A"
        exc = CyclicDependencyException(cycle_description=cycle_description)
        assert exc.status_code == 422
        assert cycle_description in str(exc.detail)

    def test_orphan_feature(self):
        """Test OrphanFeatureException."""
        feature_id = "orphan-feature"
        exc = OrphanFeatureException(feature_id=feature_id)
        assert exc.status_code == 422
        assert feature_id in str(exc.detail)


class TestRelationshipValidationExceptions:
    """Tests para excepciones de validación de relaciones."""

    def test_invalid_relation(self):
        """Test InvalidRelationException."""
        reason = "Source and target are the same"
        exc = InvalidRelationException(reason=reason)
        assert exc.status_code == 422
        assert reason in str(exc.detail)

    def test_self_relation(self):
        """Test SelfRelationException."""
        feature_id = "feature-1"
        exc = SelfRelationException(feature_id=feature_id)
        assert exc.status_code == 422
        assert feature_id in str(exc.detail)

    def test_duplicate_relation(self):
        """Test DuplicateRelationException."""
        source_id = "feature-1"
        target_id = "feature-2"
        exc = DuplicateRelationException(source_id=source_id, target_id=target_id)
        assert exc.status_code == 409
        assert source_id in str(exc.detail)
        assert target_id in str(exc.detail)

    def test_conflicting_relations(self):
        """Test ConflictingRelationsException."""
        feature1 = "feature-1"
        feature2 = "feature-2"
        exc = ConflictingRelationsException(feature1=feature1, feature2=feature2)
        assert exc.status_code == 422
        assert feature1 in str(exc.detail)
        assert feature2 in str(exc.detail)


class TestGroupValidationExceptions:
    """Tests para excepciones de validación de grupos."""

    def test_invalid_group_cardinality(self):
        """Test InvalidGroupCardinalityException."""
        exc = InvalidGroupCardinalityException(min_card=2, max_card=5, children_count=1)
        assert exc.status_code == 422
        assert "2" in str(exc.detail)
        assert "5" in str(exc.detail)
        assert "1" in str(exc.detail)

    def test_empty_group(self):
        """Test EmptyGroupException."""
        group_id = "test-group"
        exc = EmptyGroupException(group_id=group_id)
        assert exc.status_code == 422
        assert group_id in str(exc.detail)

    def test_invalid_alternative_group(self):
        """Test InvalidAlternativeGroupException."""
        reason = "Alternative group must have at least 2 children"
        exc = InvalidAlternativeGroupException(reason=reason)
        assert exc.status_code == 422
        assert reason in str(exc.detail)

    def test_invalid_or_group(self):
        """Test InvalidOrGroupException."""
        reason = "OR group cannot have max cardinality less than min"
        exc = InvalidOrGroupException(reason=reason)
        assert exc.status_code == 422
        assert reason in str(exc.detail)


class TestConstraintValidationExceptions:
    """Tests para excepciones de validación de constraints."""

    def test_invalid_constraint(self):
        """Test InvalidConstraintException."""
        expression = "Feature1 AND Feature2"
        reason = "Syntax error"
        exc = InvalidConstraintException(expression=expression, reason=reason)
        assert exc.status_code == 422
        assert expression in str(exc.detail)
        assert reason in str(exc.detail)

    def test_unsatisfiable_constraint(self):
        """Test UnsatisfiableConstraintException."""
        constraint_name = "Constraint1"
        exc = UnsatisfiableConstraintException(constraint_name=constraint_name)
        assert exc.status_code == 422
        assert constraint_name in str(exc.detail)

    def test_conflicting_constraints(self):
        """Test ConflictingConstraintsException."""
        constraint1 = "Constraint1"
        constraint2 = "Constraint2"
        exc = ConflictingConstraintsException(
            constraint1=constraint1, constraint2=constraint2
        )
        assert exc.status_code == 422
        assert constraint1 in str(exc.detail)
        assert constraint2 in str(exc.detail)


class TestConfigurationValidationExceptions:
    """Tests para excepciones de validación de configuración."""

    def test_invalid_configuration(self):
        """Test InvalidConfigurationException."""
        reason = "Configuration violates constraints"
        exc = InvalidConfigurationException(reason=reason)
        assert exc.status_code == 422
        assert reason in str(exc.detail)

    def test_mandatory_feature_missing(self):
        """Test MandatoryFeatureMissingException."""
        feature_name = "RequiredFeature"
        exc = MandatoryFeatureMissingException(feature_name=feature_name)
        assert exc.status_code == 422
        assert feature_name in str(exc.detail)

    def test_excluded_features_selected(self):
        """Test ExcludedFeaturesSelectedException."""
        feature1 = "Feature1"
        feature2 = "Feature2"
        exc = ExcludedFeaturesSelectedException(feature1=feature1, feature2=feature2)
        assert exc.status_code == 422
        assert feature1 in str(exc.detail)
        assert feature2 in str(exc.detail)

    def test_required_feature_missing(self):
        """Test RequiredFeatureMissingException."""
        source_feature = "Feature1"
        required_feature = "Feature2"
        exc = RequiredFeatureMissingException(
            source_feature=source_feature, required_feature=required_feature
        )
        assert exc.status_code == 422
        assert source_feature in str(exc.detail)
        assert required_feature in str(exc.detail)

    def test_group_cardinality_violation(self):
        """Test GroupCardinalityViolationException."""
        exc = GroupCardinalityViolationException(
            group_name="TestGroup", selected=3, min_card=1, max_card=2
        )
        assert exc.status_code == 422
        assert "TestGroup" in str(exc.detail)
        assert "3" in str(exc.detail)


class TestExportExceptions:
    """Tests para excepciones de exportación."""

    def test_unsupported_export_format(self):
        """Test UnsupportedExportFormatException."""
        format_type = "INVALID_FORMAT"
        exc = UnsupportedExportFormatException(format=format_type)
        assert exc.status_code == 400
        assert format_type in str(exc.detail)

    def test_export_failed(self):
        """Test ExportFailedException."""
        format_type = "XML"
        reason = "Missing root element"
        exc = ExportFailedException(format=format_type, reason=reason)
        assert exc.status_code == 400
        assert format_type in str(exc.detail)
        assert reason in str(exc.detail)


class TestAnalysisExceptions:
    """Tests para excepciones de análisis."""

    def test_dead_feature_detected(self):
        """Test DeadFeatureDetectedException."""
        feature_names = ["Feature1", "Feature2", "Feature3"]
        exc = DeadFeatureDetectedException(feature_names=feature_names)
        assert exc.status_code == 400
        for name in feature_names:
            assert name in str(exc.detail)

    def test_false_optional_detected(self):
        """Test FalseOptionalDetectedException."""
        feature_names = ["OptionalFeature1", "OptionalFeature2"]
        exc = FalseOptionalDetectedException(feature_names=feature_names)
        assert exc.status_code == 400
        for name in feature_names:
            assert name in str(exc.detail)


class TestExceptionInheritance:
    """Tests para verificar la herencia correcta."""

    def test_all_exceptions_inherit_from_http_exception(self):
        """Verificar que todas las excepciones heredan de HTTPException."""
        exceptions_to_test = [
            FeatureModelNotFoundException("test"),
            InvalidVersionStateException("DRAFT", "PUBLISHED", "test"),
            MissingRootFeatureException(),
            InvalidRelationException("test"),
            InvalidGroupCardinalityException(1, 2, 0),
            InvalidConstraintException("test"),
            InvalidConfigurationException("test"),
            UnsupportedExportFormatException("test"),
            DeadFeatureDetectedException(["test"]),
        ]

        for exc in exceptions_to_test:
            assert isinstance(
                exc, HTTPException
            ), f"{type(exc).__name__} should inherit from HTTPException"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
