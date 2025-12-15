from typing import Protocol, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.a_sync.feature_model_version import (
        IFeatureModelVersionRepositoryAsync,
    )


class IConstraintRepositoryAsync(Protocol):
    """Interfaz para el repositorio asíncrono de constraints."""

    async def create(
        self,
        data: ConstraintCreate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositoryAsync",
    ) -> Constraint: ...
    async def get(self, constraint_id: UUID) -> Optional[Constraint]: ...
    async def delete(
        self,
        db_constraint: Constraint,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositoryAsync",
    ) -> None: ...
    async def exists(self, constraint_id: UUID) -> bool: ...
