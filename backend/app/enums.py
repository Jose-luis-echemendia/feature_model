from enum import Enum


class UserRole(str, Enum):
    """
    Enums para definir los roles del usuario
    """

    admin = "admin"
    model_designer = "model_designer"
    teaching = "teaching"
