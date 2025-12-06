from typing import Protocol, Optional
from uuid import UUID
from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)


class IConstraintRepositoryAsync(Protocol):
    """Interfaz para el repositorio asíncrono de constraints."""

    async def create(self, data: ConstraintCreate, user: User) -> Constraint: ...
    async def get(self, constraint_id: UUID) -> Optional[Constraint]: ...
    async def delete(self, db_constraint: Constraint, user: User) -> None: ...
    async def exists(self, constraint_id: UUID) -> bool: ...
