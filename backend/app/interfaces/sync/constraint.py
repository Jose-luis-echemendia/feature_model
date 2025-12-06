from typing import Protocol, Optional, TYPE_CHECKING
from uuid import UUID
from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)

if TYPE_CHECKING:
    from app.interfaces.sync.feature_model_version import (
        IFeatureModelVersionRepositorySync,
    )


class IConstraintRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de constraints."""

    def create(
        self,
        data: ConstraintCreate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> Constraint: ...
    def get(self, constraint_id: UUID) -> Optional[Constraint]: ...
    def delete(
        self,
        db_constraint: Constraint,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> None: ...
    def exists(self, constraint_id: UUID) -> bool: ...
