import uuid
from datetime import datetime

from sqlmodel import Session, select, func
from sqlalchemy import and_


from app.models.appointment import Appointment, AppointmentCreate, AppointmentUpdate


def get_appointment_by_id(*, session: Session, id: uuid.UUID) -> Appointment | None:
    """Obtiene una cita por su ID."""
    statement = select(Appointment).where(Appointment.id == id)
    return session.exec(statement).first()


def get_appointments(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Appointment]:
    """Obtiene una lista paginada de citas."""
    statement = select(Appointment).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_appointments_count(*, session: Session) -> int:
    """Obtiene el número total de citas."""
    count_statement = select(func.count(Appointment.id))
    count = session.exec(count_statement).one()
    return count


def get_appointments_by_date_range(
    *, session: Session, start_date: datetime, end_date: datetime
) -> list[Appointment]:
    """Obtiene todas las citas dentro de un rango de fechas."""
    statement = (
        select(Appointment)
        .where(
            Appointment.start_time >= start_date, Appointment.start_time < end_date
        )  # Usar < en end_date es más común
        .order_by(Appointment.start_time)
    )
    return session.exec(statement).all()


def create_appointment_with_owner(
    *, session: Session, appointment_in: AppointmentCreate, owner_id: uuid.UUID
) -> Appointment:
    """Crea una nueva cita y la asocia con un owner (usuario)."""
    # Usamos .model_validate() que es el nuevo alias de .from_orm() en Pydantic v2
    db_appointment = Appointment.model_validate(
        appointment_in, update={"owner_id": owner_id}
    )
    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)
    return db_appointment


def update_appointment(
    *, session: Session, db_appointment: Appointment, appointment_in: AppointmentUpdate
) -> Appointment:
    """Actualiza una cita existente."""
    appointment_data = appointment_in.model_dump(exclude_unset=True)
    db_appointment.sqlmodel_update(appointment_data)
    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)
    return db_appointment


def is_timeslot_available(
    *,
    session: Session,
    start_time: datetime,
    end_time: datetime,
    appointment_id_to_exclude: uuid.UUID | None = None
) -> bool:
    """
    Verifica si un bloque de tiempo está libre.
    Lógica de solapamiento: (StartA < EndB) and (EndA > StartB)
    """
    statement = select(Appointment).where(
        and_(Appointment.start_time < end_time, Appointment.end_time > start_time)
    )
    if appointment_id_to_exclude:
        statement = statement.where(Appointment.id != appointment_id_to_exclude)

    conflicting_appointment = session.exec(statement).first()
    return conflicting_appointment is None
