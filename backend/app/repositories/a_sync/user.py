import anyio

from uuid import UUID
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, UserCreate, UserUpdate
from app.interfaces import IUserRepositoryAsync
from app.core.security import get_password_hash, verify_password
from app.repositories.base import BaseUserRepository


class UserRepositoryAsync(BaseUserRepository, IUserRepositoryAsync):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> User:
        existing = await self.get_by_email(data.email)
        self.validate_email_unique(existing)

        hashed_pw = self.prepare_password(data.password)

        obj = User(
            email=data.email, full_name=data.full_name, hashed_password=hashed_pw
        )

        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, user_id: UUID):
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        return (await self.session.exec(stmt)).first()

    async def get_all(self, skip: int = 0, limit: int = 100):
        stmt = select(User).offset(skip).limit(limit)
        return (await self.session.exec(stmt)).all()

    async def update(self, db_user: User, data: UserUpdate):
        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = self.prepare_password(
                update_data.pop("password")
            )

        db_user.sqlmodel_update(update_data)
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def delete(self, db_user: User):
        await self.session.delete(db_user)
        await self.session.commit()
        return db_user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        db_user = await self.get_by_email(email)
        if not db_user:
            return None
        # verify_password sync -> correr en thread
        ok = await anyio.to_thread.run_sync(
            verify_password, password, db_user.hashed_password
        )
        if not ok:
            return None
        return db_user

    async def change_password(
        self, db_user: User, current_password: str, new_password: str
    ) -> User:
        ok = await anyio.to_thread.run_sync(
            verify_password, current_password, db_user.hashed_password
        )
        if not ok:
            raise ValueError("La contraseña actual es incorrecta")
        db_user.hashed_password = await anyio.to_thread.run_sync(
            get_password_hash, new_password
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def exists(self, user_id: UUID) -> bool:
        return await self.session.get(User, user_id) is not None

    async def count(self) -> int:
        """Cuenta el número total de usuarios en la base de datos."""
        stmt = select(func.count()).select_from(User)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        stmt = (
            select(User)
            .where(
                (User.email.ilike(f"%{search_term}%"))
                | (User.full_name.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def deactivate(self, db_user: User) -> User:
        db_user.is_active = False
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def activate(self, db_user: User) -> User:
        db_user.is_active = True
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
