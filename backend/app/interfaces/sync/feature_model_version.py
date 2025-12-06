from typing import Protocol, Optional
from uuid import UUID
from app.models import (
    FeatureModelVersion,
    User,
)


class IFeatureModelVersionRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de versiones de feature models."""

    def get(self, version_id: UUID) -> Optional[FeatureModelVersion]: ...
    def get_latest_version_number(self, feature_model_id: UUID) -> int: ...
    def create_new_version_from_existing(
        self,
        source_version: FeatureModelVersion,
        user: User,
        return_id_map: bool = False,
    ) -> (
        FeatureModelVersion
        | tuple[FeatureModelVersion, dict[UUID, UUID], dict[UUID, UUID]]
    ): ...
    def exists(self, version_id: UUID) -> bool: ...
