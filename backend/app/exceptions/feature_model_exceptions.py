"""
Excepciones personalizadas para Feature Models.

Este módulo define excepciones específicas del dominio de Feature Models
para proporcionar mensajes de error claros y códigos HTTP apropiados.
"""

from app.exceptions import (
    NotFoundException,
    BusinessLogicException,
    UnprocessableEntityException,
    ConflictException,
)


# ========================================================================
# FEATURE MODEL EXCEPTIONS
# ========================================================================


class FeatureModelNotFoundException(NotFoundException):
    """El Feature Model solicitado no existe."""

    def __init__(self, model_id: str):
        super().__init__(detail=f"Feature Model with ID '{model_id}' not found")


class FeatureModelVersionNotFoundException(NotFoundException):
    """La versión del Feature Model solicitada no existe."""

    def __init__(self, version_id: str = None, version_number: int = None):
        if version_number is not None:
            detail = f"Feature Model version {version_number} not found"
        else:
            detail = f"Feature Model version '{version_id}' not found"
        super().__init__(detail=detail)


class FeatureNotFoundException(NotFoundException):
    """La Feature solicitada no existe."""

    def __init__(self, feature_id: str):
        super().__init__(detail=f"Feature with ID '{feature_id}' not found")


# ========================================================================
# VERSION MANAGEMENT EXCEPTIONS
# ========================================================================


class InvalidVersionStateException(BusinessLogicException):
    """La versión no está en el estado correcto para realizar la operación."""

    def __init__(self, current_state: str, required_state: str, operation: str):
        super().__init__(
            detail=f"Cannot {operation}: version is in state '{current_state}', "
            f"but '{required_state}' is required"
        )


class VersionAlreadyPublishedException(ConflictException):
    """Intento de modificar una versión ya publicada (inmutable)."""

    def __init__(self, version_id: str):
        super().__init__(
            detail=f"Version '{version_id}' is already published and cannot be modified. "
            "Published versions are immutable."
        )


class NoPublishedVersionException(NotFoundException):
    """No existe ninguna versión publicada del Feature Model."""

    def __init__(self, model_id: str):
        super().__init__(detail=f"Feature Model '{model_id}' has no published versions")


# ========================================================================
# STRUCTURAL VALIDATION EXCEPTIONS
# ========================================================================


class InvalidTreeStructureException(UnprocessableEntityException):
    """La estructura del árbol de features no es válida."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid tree structure: {reason}")


class MissingRootFeatureException(UnprocessableEntityException):
    """El Feature Model no tiene una feature raíz."""

    def __init__(self):
        super().__init__(
            detail="Feature Model must have exactly one root feature (feature without parent)"
        )


class MultipleRootFeaturesException(UnprocessableEntityException):
    """El Feature Model tiene múltiples features raíz."""

    def __init__(self, count: int):
        super().__init__(
            detail=f"Feature Model must have exactly one root feature, but found {count}"
        )


class CyclicDependencyException(UnprocessableEntityException):
    """Detectado ciclo en la estructura del árbol o en las relaciones."""

    def __init__(self, cycle_description: str = None):
        detail = "Cyclic dependency detected in feature tree"
        if cycle_description:
            detail += f": {cycle_description}"
        super().__init__(detail=detail)


class OrphanFeatureException(UnprocessableEntityException):
    """Feature sin parent que no es raíz."""

    def __init__(self, feature_id: str):
        super().__init__(
            detail=f"Feature '{feature_id}' is orphaned (no parent and not root)"
        )


# ========================================================================
# RELATIONSHIP VALIDATION EXCEPTIONS
# ========================================================================


class InvalidRelationException(UnprocessableEntityException):
    """Relación entre features no válida."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid feature relation: {reason}")


class SelfRelationException(UnprocessableEntityException):
    """Una feature no puede tener relación consigo misma."""

    def __init__(self, feature_id: str):
        super().__init__(
            detail=f"Feature '{feature_id}' cannot have a relation with itself"
        )


class DuplicateRelationException(ConflictException):
    """Ya existe una relación entre las mismas features."""

    def __init__(self, source_id: str, target_id: str):
        super().__init__(
            detail=f"Relation between '{source_id}' and '{target_id}' already exists"
        )


class ConflictingRelationsException(UnprocessableEntityException):
    """Relaciones conflictivas (ej: requires y excludes simultáneamente)."""

    def __init__(self, feature1: str, feature2: str):
        super().__init__(
            detail=f"Conflicting relations between '{feature1}' and '{feature2}'. "
            "Features cannot both require and exclude each other."
        )


# ========================================================================
# GROUP VALIDATION EXCEPTIONS
# ========================================================================


class InvalidGroupCardinalityException(UnprocessableEntityException):
    """Cardinalidades de grupo no válidas."""

    def __init__(self, min_card: int, max_card: int, children_count: int):
        super().__init__(
            detail=f"Invalid group cardinality: min={min_card}, max={max_card}, "
            f"but group has {children_count} children. "
            "Must satisfy: 0 <= min <= max <= children_count"
        )


class EmptyGroupException(UnprocessableEntityException):
    """Grupo sin features hijas."""

    def __init__(self, group_id: str):
        super().__init__(
            detail=f"Group '{group_id}' must have at least one child feature"
        )


class InvalidAlternativeGroupException(UnprocessableEntityException):
    """Grupo alternative (XOR) con configuración inválida."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid alternative group: {reason}")


class InvalidOrGroupException(UnprocessableEntityException):
    """Grupo OR con configuración inválida."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid OR group: {reason}")


# ========================================================================
# CONSTRAINT VALIDATION EXCEPTIONS
# ========================================================================


class InvalidConstraintException(UnprocessableEntityException):
    """Constraint con expresión no válida."""

    def __init__(self, expression: str, reason: str = None):
        detail = f"Invalid constraint expression: '{expression}'"
        if reason:
            detail += f". Reason: {reason}"
        super().__init__(detail=detail)


class UnsatisfiableConstraintException(UnprocessableEntityException):
    """Constraint que hace el modelo insatisfacible."""

    def __init__(self, constraint_name: str):
        super().__init__(
            detail=f"Constraint '{constraint_name}' makes the model unsatisfiable. "
            "No valid configuration can satisfy all constraints."
        )


class ConflictingConstraintsException(UnprocessableEntityException):
    """Constraints conflictivos entre sí."""

    def __init__(self, constraint1: str, constraint2: str):
        super().__init__(
            detail=f"Conflicting constraints: '{constraint1}' and '{constraint2}' "
            "cannot be satisfied simultaneously"
        )


# ========================================================================
# CONFIGURATION EXCEPTIONS
# ========================================================================


class InvalidConfigurationException(UnprocessableEntityException):
    """Configuración que viola las restricciones del modelo."""

    def __init__(self, reason: str):
        super().__init__(detail=f"Invalid configuration: {reason}")


class MandatoryFeatureMissingException(UnprocessableEntityException):
    """Falta una feature mandatory en la configuración."""

    def __init__(self, feature_name: str):
        super().__init__(
            detail=f"Mandatory feature '{feature_name}' must be selected in configuration"
        )


class ExcludedFeaturesSelectedException(UnprocessableEntityException):
    """Features con relación 'excludes' seleccionadas simultáneamente."""

    def __init__(self, feature1: str, feature2: str):
        super().__init__(
            detail=f"Features '{feature1}' and '{feature2}' exclude each other "
            "and cannot be selected together"
        )


class RequiredFeatureMissingException(UnprocessableEntityException):
    """Feature requerida no seleccionada."""

    def __init__(self, source_feature: str, required_feature: str):
        super().__init__(
            detail=f"Feature '{source_feature}' requires '{required_feature}' "
            "to be selected"
        )


class GroupCardinalityViolationException(UnprocessableEntityException):
    """Selección de features no cumple la cardinalidad del grupo."""

    def __init__(self, group_name: str, selected: int, min_card: int, max_card: int):
        super().__init__(
            detail=f"Group '{group_name}' requires between {min_card} and {max_card} "
            f"features to be selected, but {selected} were selected"
        )


# ========================================================================
# EXPORT EXCEPTIONS
# ========================================================================


class UnsupportedExportFormatException(BusinessLogicException):
    """Formato de exportación no soportado."""

    def __init__(self, format: str):
        super().__init__(
            detail=f"Export format '{format}' is not supported. "
            "Supported formats: XML, SPLOT_XML, TVL, DIMACS, JSON, UVL, DOT, MERMAID"
        )


class ExportFailedException(BusinessLogicException):
    """Error durante el proceso de exportación."""

    def __init__(self, format: str, reason: str):
        super().__init__(detail=f"Failed to export to {format}: {reason}")


# ========================================================================
# ANALYSIS EXCEPTIONS
# ========================================================================


class DeadFeatureDetectedException(BusinessLogicException):
    """Features muertas detectadas en el análisis."""

    def __init__(self, feature_names: list[str]):
        features_str = "', '".join(feature_names)
        super().__init__(
            detail=f"Dead features detected: '{features_str}'. "
            "These features can never be selected in any valid configuration."
        )


class FalseOptionalDetectedException(BusinessLogicException):
    """False optional features detectadas."""

    def __init__(self, feature_names: list[str]):
        features_str = "', '".join(feature_names)
        super().__init__(
            detail=f"False optional features detected: '{features_str}'. "
            "These features appear optional but are always selected."
        )
