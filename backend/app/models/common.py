import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# ---------------------------------------------------------------------------
# Modelos Base y Genéricos
# ---------------------------------------------------------------------------

# Define un tipo genérico para usar en PaginatedResponse
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Modelo genérico para respuestas de API que incluyen paginación.
    """

    count: int
    data: list[T]


class BaseTable(SQLModel):
    """Modelo base para tablas que incluye campos comunes como id y timestamps."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime | None = Field(default=None)


class Message(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Modelos para Autenticación y Tokens
# ---------------------------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: uuid.UUID | None = None


class NewPassword(BaseModel):
    token: str
    new_password: str


class LoginRequest(BaseModel):
    username: str
    password: str
