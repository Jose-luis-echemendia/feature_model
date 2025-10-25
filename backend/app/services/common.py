from typing import List, Dict, Type
from enum import Enum

def format_enum_for_frontend(enum_class: Type[Enum]) -> List[Dict[str, str]]:
    """
    Convierte una clase Enum en una lista de diccionarios con 'value' y 'label'.
    La etiqueta se genera automáticamente a partir del valor.
    Ej: 'poco_hecha' -> 'Poco Hecha'
    """
    options = []
    for member in enum_class:
        # Crea una etiqueta legible para el frontend
        label = member.value.replace('_', ' ').title()
        options.append({"value": member.value, "label": label})
    return options