import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import AsyncConfigurationRepoDep
from app.models.configuration import (
    ConfigurationCreate,
    ConfigurationPublic,
    ConfigurationPublicWithFeatures,
    ConfigurationUpdate,
)

router = APIRouter()


@router.post("/", response_model=ConfigurationPublic)
async def create_configuration(
    *,
    configuration_in: ConfigurationCreate,
    configuration_repo: AsyncConfigurationRepoDep,
) -> ConfigurationPublic:
    """
    Crea una nueva configuración.
    """
    configuration = await configuration_repo.create(data=configuration_in)
    return configuration


@router.get("/{id}", response_model=ConfigurationPublicWithFeatures)
async def read_configuration(
    *,
    id: uuid.UUID,
    configuration_repo: AsyncConfigurationRepoDep,
) -> ConfigurationPublicWithFeatures:
    """
    Obtiene una configuración por su ID.
    """
    db_configuration = await configuration_repo.get(configuration_id=id)
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return db_configuration


@router.put("/{id}", response_model=ConfigurationPublic)
async def update_configuration(
    *,
    id: uuid.UUID,
    configuration_in: ConfigurationUpdate,
    configuration_repo: AsyncConfigurationRepoDep,
) -> ConfigurationPublic:
    """
    Actualiza una configuración.
    """
    db_configuration = await configuration_repo.get(configuration_id=id)
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")

    db_configuration = await configuration_repo.update(
        db_configuration=db_configuration,
        data=configuration_in,
    )
    return db_configuration
