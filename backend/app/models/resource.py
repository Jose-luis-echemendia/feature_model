import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, Union
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB

from .common import BaseTable
from app.models import UserPublic
from app.enums import ResourceType, ResourceStatus, LicenseType

if TYPE_CHECKING:
    from .feature import Feature
    from .user import User


# --- Modelo Base Mejorado ---
class ResourceBase(SQLModel):
    # --- Metadatos Fundamentales ---
    title: str = Field(
        index=True,
        max_length=255,
        description="Título principal del recurso, visible para el usuario.",
    )
    type: ResourceType = Field(
        description="El tipo de recurso (video, pdf, quiz, etc.)."
    )
    content_url_or_data: str | dict = Field(
        description="URL, contenido embebido o JSON que define el recurso."
    )

    # --- Metadatos Descriptivos ---
    description: Optional[str] = Field(
        default=None,
        description="Una breve sinopsis o resumen del contenido del recurso.",
    )
    language: str = Field(
        default="es",
        max_length=10,
        description="Idioma principal del contenido (ej. 'es', 'en-US').",
    )
    duration_minutes: Optional[int] = Field(
        default=None,
        description="Duración estimada en minutos para completar/consumir el recurso.",
    )

    # --- Metadatos de Gestión y Ciclo de Vida ---
    version: int = Field(
        default=1,
        description="Versión del recurso para controlar cambios y actualizaciones.",
    )
    status: ResourceStatus = Field(
        default=ResourceStatus.DRAFT,
        description="Estado del ciclo de vida del recurso (borrador, publicado, etc.).",
    )
    publication_date: Optional[date] = Field(
        default=None,
        description="Fecha en que el recurso fue publicado o considerado 'estable'.",
    )

    # --- Metadatos de Autoría y Propiedad ---
    author_name: Optional[str] = Field(
        default=None,
        description="Nombre del autor o creador del contenido (texto libre).",
    )
    owner_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id",
        description="ID del usuario propietario del recurso dentro de la plataforma.",
    )

    # --- Metadatos de Licenciamiento y Uso ---
    license: LicenseType = Field(
        default=LicenseType.INTERNAL_USE,
        description="Tipo de licencia que rige el uso del recurso.",
    )
    valid_until: Optional[date] = Field(
        default=None,
        description="Fecha de caducidad de la licencia o del contenido (si aplica).",
    )

    # --- Metadatos de Accesibilidad y Técnicos ---
    tags: list[str] = Field(
        default=[],
        sa_column=Column(JSONB),
        description="Etiquetas de formato libre para búsqueda (ej. 'algebra', 'introduccion', 'python3.9').",
    )
    accessibility_notes: Optional[str] = Field(
        default=None,
        description="Notas sobre características de accesibilidad (ej. 'subtítulos en español', 'compatible con lector de pantalla').",
    )


# --- Modelo de Base de Datos ---
class Resource(BaseTable, ResourceBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------------

    __tablename__ = "resources"

    # ------------------ RELATIONSHIP ----------------------------------------

    # Relación de vuelta para saber en qué features se usa este recurso
    features: list["Feature"] = Relationship(back_populates="resource")

    # Relación con el usuario propietario
    owner: Optional["User"] = Relationship()


# --- Modelos Pydantic para la API ---
class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(SQLModel):
    # Definimos qué campos se pueden actualizar, todos opcionales
    title: Optional[str] = None
    type: Optional[ResourceType] = None
    content_url_or_data: Optional[Union[str, dict]] = None
    description: Optional[str] = None
    language: Optional[str] = None
    duration_minutes: Optional[int] = None
    version: Optional[int] = None
    status: Optional[ResourceStatus] = None
    publication_date: Optional[date] = None
    author_name: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None
    license: Optional[LicenseType] = None
    valid_until: Optional[date] = None
    tags: Optional[list[str]] = None
    accessibility_notes: Optional[str] = None


class ResourcePublic(ResourceBase):
    id: uuid.UUID
    created_at: datetime
    owner: Optional[UserPublic] = None
