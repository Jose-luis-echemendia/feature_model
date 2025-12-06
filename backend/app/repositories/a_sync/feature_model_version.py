import uuid
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Feature,
    FeatureModelVersion,
    FeatureGroup,
    Constraint,
    FeatureRelation,
    User,
)
from app.interfaces import IFeatureModelVersionRepositoryAsync
from app.repositories.base import BaseFeatureModelVersionRepository


class FeatureModelVersionRepositoryAsync(
    BaseFeatureModelVersionRepository, IFeatureModelVersionRepositoryAsync
):
    """Implementación asíncrona del repositorio de versiones de feature models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, version_id: uuid.UUID) -> FeatureModelVersion | None:
        """Obtener una versión de modelo por su ID."""
        stmt = select(FeatureModelVersion).where(FeatureModelVersion.id == version_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_version_number(self, feature_model_id: uuid.UUID) -> int:
        """Obtener el número de la última versión para un modelo."""
        statement = select(FeatureModelVersion.version_number).where(
            FeatureModelVersion.feature_model_id == feature_model_id
        )
        result = await self.session.execute(statement)
        versions = result.all()
        return max((v[0] for v in versions), default=0)

    async def create_new_version_from_existing(
        self,
        source_version: FeatureModelVersion,
        user: User,
        return_id_map: bool = False,
    ) -> (
        FeatureModelVersion
        | tuple[
            FeatureModelVersion, dict[uuid.UUID, uuid.UUID], dict[uuid.UUID, uuid.UUID]
        ]
    ):
        """
        Crea una nueva versión de un modelo de características, clonando todas las
        features y relaciones de una versión de origen. (Copy-On-Write)

        Nota: Utiliza run_sync para ejecutar la lógica sync del repositorio.
        """

        def _create_version_sync(sync_session):
            from app.repositories.sync.feature_model_version import (
                FeatureModelVersionRepositorySync,
            )

            sync_repo = FeatureModelVersionRepositorySync(sync_session)
            return sync_repo.create_new_version_from_existing(
                source_version=source_version,
                user=user,
                return_id_map=return_id_map,
            )

        # Ejecutar la lógica sync dentro del contexto async
        result = await self.session.run_sync(_create_version_sync)
        return result

    async def exists(self, version_id: uuid.UUID) -> bool:
        """Verificar si una versión existe."""
        version = await self.get(version_id)
        return version is not None
