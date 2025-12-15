"""Modelos y esquemas relacionados con usuarios de la plataforma.

Define la entidad `User` (tabla `users`) junto con los modelos auxiliares
para creación, actualización y respuestas públicas. Incluye relaciones de
auditoría y asociaciones con feature models (propiedad/colaboración).
"""

import uuid
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship


# --- imports APP ---
from app.enums import UserRole
from .common import BaseTable, PaginatedResponse
from .link_models import FeatureModelCollaborator

if TYPE_CHECKING:
    from .feature_model import FeatureModel

# ========================================================================
#           --- Modelo de Usuario base ---
# ========================================================================

# Shared properties
class UserBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_superuser: bool = False
    role: UserRole = Field(default=UserRole.VIEWER)


# ========================================================================
#           --- Modelo para la tabla física de User ---
# ========================================================================
# Database model, database table inferred from class name
class User(BaseTable, UserBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "users"

    hashed_password: str

    # ------------------ RELATIONSHIP ----------------------------------------
    # --- audit fields ---

    # Relación para el usuario que creó este registro (many-to-one)
    created_by: Optional["User"] = Relationship(
        back_populates="created_users",
        sa_relationship_kwargs={
            "foreign_keys": "User.created_by_id",
            "remote_side": "User.id",
        },
    )

    # Relación para el usuario que actualizó este registro (many-to-one)
    updated_by: Optional["User"] = Relationship(
        back_populates="updated_users",
        sa_relationship_kwargs={
            "foreign_keys": "User.updated_by_id",
            "remote_side": "User.id",
        },
    )

    # Relación para el usuario que eliminó este registro (many-to-one)
    deleted_by: Optional["User"] = Relationship(
        back_populates="deleted_users",
        sa_relationship_kwargs={
            "foreign_keys": "User.deleted_by_id",
            "remote_side": "User.id",
        },
    )

    # Relación inversa (one-to-many)
    created_users: list["User"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={"foreign_keys": "User.created_by_id"},
    )

    updated_users: list["User"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={"foreign_keys": "User.updated_by_id"},
    )

    deleted_users: list["User"] = Relationship(
        back_populates="deleted_by",
        sa_relationship_kwargs={"foreign_keys": "User.deleted_by_id"},
    )

    # Modelos en los que este usuario es un propietario de un modelo
    owned_feature_models: list["FeatureModel"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"foreign_keys": "[FeatureModel.owner_id]"},
    )

    # Modelos en los que este usuario es un colaborador
    collaborating_feature_models: list["FeatureModel"] = Relationship(
        back_populates="collaborators", link_model=FeatureModelCollaborator
    )


# ========================================================================
#           --- Modelos para Entrada de datos de Usuario ---
# ========================================================================


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# ========================================================================
#           --- Modelos para Respuestas de Usuario ---
# ========================================================================


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UserListResponse(PaginatedResponse[UserPublic]):
    """
    Respuesta para listar los usuarios.
    """

    pass
