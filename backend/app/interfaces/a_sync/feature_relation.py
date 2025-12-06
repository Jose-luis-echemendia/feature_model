from typing import Protocol, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    FeatureRelation,
    FeatureRelationCreate,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.a_sync.feature import IFeatureRepositoryAsync


class IFeatureRelationRepositoryAsync(Protocol):
    """Interfaz para el repositorio asíncrono de relaciones entre features."""

    async def create(
        self,
        data: FeatureRelationCreate,
        user: User,
        feature_repo: "IFeatureRepositoryAsync",
    ) -> FeatureRelation: ...
    async def get(self, relation_id: UUID) -> Optional[FeatureRelation]: ...
    async def delete(self, db_relation: FeatureRelation, user: User) -> None: ...
    async def exists(self, relation_id: UUID) -> bool: ...
