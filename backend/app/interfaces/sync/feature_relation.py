from typing import Protocol, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    FeatureRelation,
    FeatureRelationCreate,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.sync.feature import IFeatureRepositorySync


class IFeatureRelationRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de relaciones entre features."""

    def create(
        self,
        data: FeatureRelationCreate,
        user: User,
        feature_repo: "IFeatureRepositorySync",
    ) -> FeatureRelation: ...
    def get(self, relation_id: UUID) -> Optional[FeatureRelation]: ...
    def delete(self, db_relation: FeatureRelation, user: User) -> None: ...
    def exists(self, relation_id: UUID) -> bool: ...
