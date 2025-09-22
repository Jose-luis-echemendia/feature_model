from enum import Enum


class UserRole(str, Enum):
    """
    Enums para definir los roles del usuario
    """

    admin = "admin"
    model_designer = "model_designer"
    teaching = "teaching"

class FeatureType(str, Enum):
    """
    Tipo de una característica dentro de un Feature Model.
    - mandatory: Obligatoria, siempre debe estar presente.
    - optional: Opcional, puede o no ser seleccionada.
    - alternative: Grupo de características donde solo una puede ser elegida.
    - or: Grupo de características donde al menos una debe ser elegida.
    """
    mandatory = "mandatory"
    optional = "optional"
    alternative = "alternative"
    or_group = "or"  # Usamos or_group para evitar conflicto con la palabra clave 'or'


class RelationType(str, Enum):
    """
    Tipo de relación entre dos características.
    - requires: Una característica requiere de otra.
    - excludes: Una característica es incompatible con otra.
    """
    requires = "requires"
    excludes = "excludes"