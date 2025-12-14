from typing import Protocol, Optional
from uuid import UUID
from app.models import (
    FeatureModelVersion,
    User,
)


class IFeatureModelVersionRepositoryAsync(Protocol):
    """Interfaz para el repositorio asíncrono de versiones de feature models."""

    async def get(self, version_id: UUID) -> Optional[FeatureModelVersion]: ...
    async def get_latest_version_number(self, feature_model_id: UUID) -> int: ...
    async def create_new_version_from_existing(
        self,
        source_version: FeatureModelVersion,
        user: User,
        return_id_map: bool = False,
    ) -> (
        FeatureModelVersion
        | tuple[FeatureModelVersion, dict[UUID, UUID], dict[UUID, UUID]]
    ): ...
    async def exists(self, version_id: UUID) -> bool: ...
    async def get_complete_with_relations(
        self, version_id: UUID, include_resources: bool = True
    ) -> Optional[FeatureModelVersion]: ...
    async def get_statistics(self, version_id: UUID) -> Optional[dict[str, int]]: ...
