import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud 
from app.api import deps
from app.core.config import settings
from app.models.appointment import AppointmentPublic, WebhookAppointmentCreate

router = APIRouter()

@router.post("/n8n", response_model=AppointmentPublic, status_code=status.HTTP_201_CREATED)
def create_cita_from_webhook(
    *,
    session: Session = Depends(deps.get_db),
    cita_in: WebhookAppointmentCreate,
    api_key: str = Depends(deps.get_api_key)
):
    """Endpoint para que n8n cree una nueva cita."""
    # Llama a la función específica del módulo crud
    is_available = crud.is_timeslot_available(
        session=session, start_time=cita_in.start_time, end_time=cita_in.end_time
    )
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El horario solicitado ya no está disponible.",
        )

    first_superuser = crud.get_user_by_email(session=session, email=settings.FIRST_SUPERUSER)
    if not first_superuser:
        raise HTTPException(status_code=500, detail="No se encontró un superadministrador.")

    # Llama a la función específica del módulo crud
    cita = crud.create_cita_with_owner(session=session, cita_in=cita_in, owner_id=first_superuser.id)
    return cita