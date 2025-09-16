# endpoints for Appointments

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud
from app.api import deps
from app.models.user import User
from app.models.appointment import AppointmentPublic, AppointmentsPublic, AppointmentCreate, AppointmentUpdate

router = APIRouter()

@router.get("/", response_model=AppointmentsPublic)
def read_appointments(
    session: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    current_user: User = Depends(deps.get_current_user),
):
    """Obtener lista de citas, con opción de filtrar por fecha."""
    if start_date and end_date:
        appointments_list = crud.get_appointments_by_date_range(session=session, start_date=start_date, end_date=end_date)
        # Para rangos de fechas, el conteo es sobre el resultado. No paginamos aquí por simplicidad.
        count = len(appointments_list)
    else:
        appointments_list = crud.get_appointments(session=session, skip=skip, limit=limit)
        count = crud.get_appointments_count(session=session)
    return AppointmentsPublic(data=appointments_list, count=count)

@router.post("/", response_model=AppointmentPublic, status_code=status.HTTP_201_CREATED)
def create_appointment(
    *,
    session: Session = Depends(deps.get_db),
    appointment_in: AppointmentCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """Crear una nueva cita manualmente desde el dashboard."""
    if appointment_in.start_time >= appointment_in.end_time:
        raise HTTPException(status_code=400, detail="La hora de fin debe ser posterior a la de inicio.")

    is_available = crud.is_timeslot_available(
        session=session, start_time=appointment_in.start_time, end_time=appointment_in.end_time
    )
    if not is_available:
        raise HTTPException(status_code=409, detail="El horario solicitado está ocupado.")

    appointment = crud.create_appointment_with_owner(session=session, appointment_in=appointment_in, owner_id=current_user.id)
    return appointment

@router.put("/{id}", response_model=AppointmentPublic)
def update_appointment(
    *,
    session: Session = Depends(deps.get_db),
    id: uuid.UUID,
    appointment_in: AppointmentUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    """Actualizar una cita."""
    db_appointment = crud.get_appointment_by_id(session=session, id=id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Validar horario si se está actualizando
    if appointment_in.start_time or appointment_in.end_time:
        new_start = appointment_in.start_time or db_appointment.start_time
        new_end = appointment_in.end_time or db_appointment.end_time
        if new_start >= new_end:
            raise HTTPException(status_code=400, detail="La hora de fin debe ser posterior a la de inicio.")
        
        is_available = crud.is_timeslot_available(
            session=session, start_time=new_start, end_time=new_end, appointment_id_to_exclude=id
        )
        if not is_available:
            raise HTTPException(status_code=409, detail="El nuevo horario está ocupado.")

    appointment = crud.update_appointment(session=session, db_appointment=db_appointment, appointment_in=appointment_in)
    return appointment