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

    Attributes:
        data: Los ítems de la página actual
        count: El número total de ítems que coinciden con los filtros (sin paginación)
        page: El número de la página actual (basado en skip/limit)
        size: El número de ítems en esta página específica
        total_pages: El número total de páginas disponibles
        has_next: Indica si hay una página siguiente
        has_prev: Indica si hay una página anterior
    """

    data: list[T]  # Los ítems de la página actual
    count: int  # El número total de ítems que coinciden con los filtros
    page: int  # El número de la página actual (1-indexed)
    size: int  # El número de ítems en esta página
    total_pages: int  # El número total de páginas
    has_next: bool  # ¿Hay página siguiente?
    has_prev: bool  # ¿Hay página anterior?

    @classmethod
    def create(
        cls,
        data: list[T],
        count: int,
        skip: int = 0,
        limit: int = 100,
    ) -> "PaginatedResponse[T]":
        """
        Método helper para crear una respuesta paginada con todos los campos calculados.

        Args:
            data: Lista de ítems de la página actual
            count: Total de ítems que coinciden con los filtros
            skip: Número de ítems omitidos (offset)
            limit: Tamaño máximo de página

        Returns:
            PaginatedResponse con todos los campos calculados
        """
        import math

        # Calcular número de página (1-indexed)
        page = (skip // limit) + 1 if limit > 0 else 1

        # Número de ítems en esta página
        size = len(data)

        # Total de páginas
        total_pages = math.ceil(count / limit) if limit > 0 and count > 0 else 0

        # Indicadores de navegación
        has_next = (skip + limit) < count
        has_prev = skip > 0

        return cls(
            count=count,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            data=data,
        )


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
