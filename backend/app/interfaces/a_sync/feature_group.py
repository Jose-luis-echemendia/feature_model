from typing import Protocol, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    FeatureGroup,
    FeatureGroupCreate,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.a_sync.feature import IFeatureRepositoryAsync


class IFeatureGroupRepositoryAsync(Protocol):
    """Interfaz para el repositorio asíncrono de grupos de features."""

    async def create(
        self,
        data: FeatureGroupCreate,
        user: User,
        feature_repo: "IFeatureRepositoryAsync",
    ) -> FeatureGroup: ...
    async def get(self, group_id: UUID) -> Optional[FeatureGroup]: ...
    async def delete(self, db_group: FeatureGroup, user: User) -> None: ...
    async def exists(self, group_id: UUID) -> bool: ...
