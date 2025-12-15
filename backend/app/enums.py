from enum import Enum


class UserRole(str, Enum):
    """
    Enums para definir los roles del usuario
    """

    DEVELOPER = "developer"
    ADMIN = "admin"
    MODEL_DESIGNER = "model_designer"
    MODEL_EDITOR = "model_editor"
    CONFIGURATOR = "configurator"
    VIEWER = "viewer"
    REVIEWER = "reviewer"


class ResourceType(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    QUIZ = "quiz"
    EXTERNAL_LINK = "external_link"
    TEXT_CONTENT = "text_content"
    PACKAGE = "package"  # Conjunto de archivos/recursos agrupados


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
    CREATIVE_COMMONS_BY_SA = "cc_by_sa"  # CC - Atribución-CompartirIgual
    PUBLIC_DOMAIN = "public_domain"  # Dominio Público
    INTERNAL_USE = "internal_use"  # Solo para uso interno de la organización


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


class ModelStatus(str, Enum):
    DRAFT = "draft"  # En proceso de diseño, solo visible para su creador (y admins).
    IN_REVIEW = "in_review"  # Listo para revisión, visible para los REVIEWERS.
    PUBLISHED = "published"  # Aprobado y visible para los CONFIGURATORS.
    ARCHIVED = "archived"  # Obsoleto, ya no se puede usar para nuevas configuraciones.


class ExportFormat(str, Enum):
    """
    Formatos disponibles para exportar un Feature Model.
    """

    XML = "xml"  # FeatureIDE XML format
    SPLOT_XML = "splot_xml"  # SPLOT XML format
    TVL = "tvl"  # Textual Variability Language
    DIMACS = "dimacs"  # DIMACS CNF format for SAT solvers
    JSON = "json"  # Simple JSON format
    UVL = "uvl"  # Universal Variability Language
    DOT = "dot"  # Graphviz DOT format
    MERMAID = "mermaid"  # Mermaid diagram format


class AnalysisType(str, Enum):
    """Tipos de análisis estructural disponibles."""

    DEAD_FEATURES = "dead_features"
    REDUNDANCIES = "redundancies"
    IMPLICIT_RELATIONS = "implicit_relations"
    TRANSITIVE_DEPENDENCIES = "transitive_dependencies"
    STRONGLY_CONNECTED = "strongly_connected"
    COMPLEXITY_METRICS = "complexity_metrics"
    

class GenerationStrategy(str, Enum):
    """Estrategias de generación disponibles."""

    GREEDY = "greedy"  # Selección golosa por prioridad
    RANDOM = "random"  # Selección aleatoria válida
    BEAM_SEARCH = "beam_search"  # Búsqueda en haz
    GENETIC = "genetic"  # Algoritmos genéticos (futuro)
    
    