import uuid
from datetime import datetime
from typing import Generic, TypeVar, TYPE_CHECKING, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from .user import User

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
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, index=True)

    # Campos de auditoría de usuario
    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    updated_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    created_by: Optional["User"] = Field(default=None, foreign_key="users.id")
    updated_by: Optional["User"] = Field(default=None, foreign_key="users.id")


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
