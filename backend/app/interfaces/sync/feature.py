from typing import Protocol, List, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    Feature,
    FeatureCreate,
    FeatureUpdate,
    FeaturePublicWithChildren,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.sync import (
        IFeatureModelVersionRepositorySync,
        IFeatureGroupRepositorySync,
    )


class IFeatureRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de features."""

    def create(
        self,
        data: FeatureCreate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> Feature: ...
    def get(self, feature_id: UUID) -> Optional[Feature]: ...
    def get_by_version(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Feature]: ...
    def get_as_tree(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[FeaturePublicWithChildren]: ...
    def update(
        self,
        db_feature: Feature,
        data: FeatureUpdate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
        feature_group_repo: "IFeatureGroupRepositorySync",
    ) -> Feature: ...
    def delete(
        self,
        db_feature: Feature,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> None: ...
    def exists(self, feature_id: UUID) -> bool: ...
    def count(self, feature_model_version_id: Optional[UUID] = None) -> int: ...
