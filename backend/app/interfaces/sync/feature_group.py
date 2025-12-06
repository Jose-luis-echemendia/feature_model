from typing import Protocol, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    FeatureGroup,
    FeatureGroupCreate,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.sync.feature import IFeatureRepositorySync
    from app.interfaces.sync.feature_model_version import (
        IFeatureModelVersionRepositorySync,
    )


class IFeatureGroupRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de grupos de features."""

    def create(
        self,
        data: FeatureGroupCreate,
        user: User,
        feature_repo: "IFeatureRepositorySync",
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> FeatureGroup: ...
    def get(self, group_id: UUID) -> Optional[FeatureGroup]: ...
    def delete(
        self,
        db_group: FeatureGroup,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> None: ...
    def exists(self, group_id: UUID) -> bool: ...
