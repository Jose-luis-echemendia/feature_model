import uuid

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

# Previene importación circular al resolver los type hints
if TYPE_CHECKING:
    from .user import User


# Propiedades compartidas, usadas como base
class AppointmentBase(SQLModel):
    full_name: str = Field(index=True, max_length=255)
    phone_number: str = Field(index=True, max_length=50)
    service: str = Field(max_length=255)
    start_time: datetime
    end_time: datetime


# El modelo de la tabla de la base de datos
class Appointment(AppointmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    owner_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="appointments")


# Propiedades para recibir al crear una Appointment
class AppointmentCreate(AppointmentBase):
    pass


# Propiedades que se devolverán al cliente
class AppointmentPublic(AppointmentBase):
    id: uuid.UUID
    owner_id: uuid.UUID | None


# Propiedades para recibir al actualizar (todos los campos opcionales)
class AppointmentUpdate(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    service: str | None = Field(default=None, max_length=255)
    start_time: datetime | None = None
    end_time: datetime | None = None


# Esquema específico para el webhook (es idéntico a AppointmentCreate, pero lo mantenemos por claridad)
class WebhookAppointmentCreate(AppointmentBase):
    pass


# Modelo para devolver una lista de Appointments con paginación/conteo
class AppointmentsPublic(SQLModel):
    data: list[AppointmentPublic]
    count: int
