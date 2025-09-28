from enum import Enum


class UserRole(str, Enum):
    """
    Enums para definir los roles del usuario
    """

    ADMIN = "admin"
    MODEL_DESIGNER = "model_designer"
    CONFIGURATOR = "configurator"
    VIEWER = "viewer"


class FeatureType(str, Enum):
    """
    Tipo de una característica dentro de un Feature Model.
    - mandatory: Obligatoria, siempre debe estar presente.
    - optional: Opcional, puede o no ser seleccionada.
    - alternative: Grupo de características donde solo una puede ser elegida.
    - or: Grupo de características donde al menos una debe ser elegida.
    """

    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    ALTERNATIVE = "alternative"
    OR = "or"


class RelationType(str, Enum):
    """
    Tipo de relación entre dos características.
    - requires: Una característica requiere de otra.
    - excludes: Una característica es incompatible con otra.
    """

    REQUIRED = "requires"
    EXCLUDES = "excludes"
