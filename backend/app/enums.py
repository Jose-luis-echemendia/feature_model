from enum import Enum


class UserRole(str, Enum):
    """
    Enums para definir los roles del usuario
    """

    ADMIN = "admin"
    MODEL_DESIGNER = "model_designer"
    CONFIGURATOR = "configurator"
    VIEWER = "viewer"


class ResourceType(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    QUIZ = "quiz"
    EXTERNAL_LINK = "external_link"
    TEXT_CONTENT = "text_content"


class ResourceStatus(str, Enum):
    """Estado del ciclo de vida de un recurso."""
    DRAFT = "draft"  # Borrador, no listo para producción
    IN_REVIEW = "in_review"  # Esperando aprobación
    PUBLISHED = "published"  # Activo y disponible para ser usado
    ARCHIVED = "archived"  # Obsoleto, no se recomienda para nuevos cursos

class LicenseType(str, Enum):
    """Tipo de licencia del recurso."""
    COPYRIGHT = "copyright"  # Todos los derechos reservados
    CREATIVE_COMMONS_BY = "cc_by"  # Creative Commons - Atribución
    CREATIVE_COMMONS_BY_SA = "cc_by_sa" # CC - Atribución-CompartirIgual
    PUBLIC_DOMAIN = "public_domain" # Dominio Público
    INTERNAL_USE = "internal_use" # Solo para uso interno de la organización

class FeatureType(str, Enum):
    """
    Tipo de una característica dentro de un Feature Model.
    - mandatory: Obligatoria, siempre debe estar presente.
    - optional: Opcional, puede o no ser seleccionada.
    """

    MANDATORY = "mandatory"
    OPTIONAL = "optional"


class FeatureGroupType(str, Enum):
    """
    Tipos de grupos de características.
    alternative (XOR): Solo se puede elegir una de las características del grupo.
    or (OR): Se puede elegir una o más características del grupo.
    """

    ALTERNATIVE = "alternative"
    OR = "or"


class FeatureRelationType(str, Enum):
    """
    Tipo de relación entre dos características.
    - requires: Una característica requiere de otra.
    - excludes: Una característica es incompatible con otra.
    """

    REQUIRED = "requires"
    EXCLUDES = "excludes"
