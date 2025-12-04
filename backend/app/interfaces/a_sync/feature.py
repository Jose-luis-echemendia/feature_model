from typing import Protocol, List, Optional
from uuid import UUID
from app.models import (
    Feature,
    FeatureCreate,
    FeatureUpdate,
    FeaturePublicWithChildren,
    User,
)


class IFeatureRepositoryAsync(Protocol):
    """Interfaz para el repositorio asíncrono de features."""

    async def create(self, data: FeatureCreate, user: User) -> Feature: ...
    async def get(self, feature_id: UUID) -> Optional[Feature]: ...
    async def get_by_version(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Feature]: ...
    async def get_as_tree(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[FeaturePublicWithChildren]: ...
    async def update(
        self, db_feature: Feature, data: FeatureUpdate, user: User
    ) -> Feature: ...
    async def delete(self, db_feature: Feature, user: User) -> None: ...
    async def exists(self, feature_id: UUID) -> bool: ...
    async def count(self, feature_model_version_id: Optional[UUID] = None) -> int: ...
