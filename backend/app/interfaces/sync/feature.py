from typing import Protocol, List, Optional
from uuid import UUID
from app.models import (
    Feature,
    FeatureCreate,
    FeatureUpdate,
    FeaturePublicWithChildren,
    User,
)


class IFeatureRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de features."""

    def create(self, data: FeatureCreate, user: User) -> Feature: ...
    def get(self, feature_id: UUID) -> Optional[Feature]: ...
    def get_by_version(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Feature]: ...
    def get_as_tree(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[FeaturePublicWithChildren]: ...
    def update(
        self, db_feature: Feature, data: FeatureUpdate, user: User
    ) -> Feature: ...
    def delete(self, db_feature: Feature, user: User) -> None: ...
    def exists(self, feature_id: UUID) -> bool: ...
    def count(self, feature_model_version_id: Optional[UUID] = None) -> int: ...
