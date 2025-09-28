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
