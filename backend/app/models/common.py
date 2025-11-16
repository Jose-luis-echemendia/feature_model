"""Modelos comunes y esquemas genéricos usados por otros modelos.

Este módulo define las clases base compartidas (por ejemplo `BaseTable`),
modelos de paginación y respuestas estándar (errores/éxitos/tokens) que se
utilizan a lo largo de la API. Mantener aquí los tipos reutilizables ayuda a
evitar duplicación y facilita la consistencia de las respuestas.
"""

import uuid
from datetime import datetime
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


# ========================================================================
#              --- Modelos Base y Genéricos ---
# ========================================================================

# Define un tipo genérico para usar en PaginatedResponse
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Modelo genérico para respuestas de API que incluyen paginación.
    """

    total: int  # El número total de ítems en la base de datos.
    page: int  # El número de la página actual que se está devolviendo.
    size: int  # El número de ítems en esta página específica (puede ser menor que el 'limit').
    data: list[T]  # Los ítems de la página actual.


class BaseTable(SQLModel):
    """Modelo base para tablas que incluye campos comunes como id y timestamps."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, index=True)  # is_deleted

    # Campos de auditoría de usuario
    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    updated_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    deleted_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")


class Message(BaseModel):
    message: str


# ========================================================================
#           --- Modelos para Autenticación y Tokens ---
# ========================================================================


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[uuid.UUID] = None


class NewPassword(BaseModel):
    token: str
    new_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Usamos TypeVar para crear un tipo genérico que pueda contener cualquier dato
DataType = TypeVar("DataType")


# ========================================================================
#              --- Modelo para respuestas de la API ---
# ========================================================================


# ========================================================================
#                 --- Modelo para Errores ---
# ========================================================================
class ErrorDetail(BaseModel):
    http_code: int
    error_code: int
    category: str
    description: str
    request_id: str


class ErrorResponse(BaseModel):
    object: str
    code: int
    status: str = "error"
    message: ErrorDetail


# ========================================================================
#                       --- Modelo para Éxitos ---
# ========================================================================


# Este es un modelo genérico. `data` puede ser un User, una lista de Products, etc.
class SuccessResponse(BaseModel, Generic[DataType]):
    object: str
    code: int = 200
    status: str = "success"
    data: DataType


# ========================================================================
#              --- Modelo para los ENUMS del sistema ---
# ========================================================================


class EnumValue(BaseModel):
    """Modelo para representar un par valor/etiqueta de un enum."""

    value: str
    label: str


class AllEnumsResponse(BaseModel):
    """Modelo de respuesta que contiene todas las listas de enums."""

    userRoles: list[EnumValue]
    productCategories: list[EnumValue]
    orderStatuses: list[EnumValue]
    pizzaBakingOptions: list[EnumValue]
    genericSizes: list[EnumValue]
