import uuid

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import SessionDep
from app.models import (
    ConfigurationCreate,
    ConfigurationPublic,
    ConfigurationPublicWithFeatures,
    ConfigurationUpdate,
    Message,
)

router = APIRouter()


@router.post("/", response_model=ConfigurationPublic)
def create_configuration(*, session: SessionDep, configuration_in: ConfigurationCreate):
    """
    Crea una nueva configuración.
    """
    configuration = crud.create_configuration(
        session=session, configuration_create=configuration_in
    )
    return configuration


@router.get("/{id}", response_model=ConfigurationPublicWithFeatures)
def read_configuration(*, session: SessionDep, id: uuid.UUID):
    """
    Obtiene una configuración por su ID.
    """
    db_configuration = crud.get_configuration_by_id(
        session=session, configuration_id=id
    )
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return db_configuration


@router.put("/{id}", response_model=ConfigurationPublic)
def update_configuration(
    *, session: SessionDep, id: uuid.UUID, configuration_in: ConfigurationUpdate
):
    """
    Actualiza una configuración.
    """
    db_configuration = crud.get_configuration_by_id(
        session=session, configuration_id=id
    )
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    db_configuration = crud.update_configuration(
        session=session, db_obj=db_configuration, obj_in=configuration_in
    )
    return db_configuration
