from typing import Protocol, Optional
from uuid import UUID
from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)


class IConstraintRepositorySync(Protocol):
    """Interfaz para el repositorio síncrono de constraints."""

    def create(self, data: ConstraintCreate, user: User) -> Constraint: ...
    def get(self, constraint_id: UUID) -> Optional[Constraint]: ...
    def delete(self, db_constraint: Constraint, user: User) -> None: ...
    def exists(self, constraint_id: UUID) -> bool: ...
