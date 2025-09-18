from enum import Enum


class UserRole(str, Enum):
    """
    Enums para definir los roles del usuario
    """
    admin: str = "admin"
    model_designer: str = "model_designer"
    teaching: str = "teaching"
    