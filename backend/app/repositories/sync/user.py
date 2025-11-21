import anyio

from uuid import UUID
from typing import Optional
from sqlmodel import select, Session, func

from app.models import User, UserCreate, UserUpdate
from app.interfaces import IUserRepositorySync
from app.core.security import get_password_hash, verify_password
from app.repositories.base import BaseUserRepository


class UserRepositorySync(BaseUserRepository, IUserRepositorySync):

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: UserCreate) -> User:
        # verificar email
        existing = self.get_by_email(data.email)
        self.validate_email_unique(existing)

        hashed_pw = self.prepare_password(data.password)

        obj = User(
            email=data.email, full_name=data.full_name, hashed_password=hashed_pw
        )

        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.exec(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return self.session.exec(stmt).all()

    def update(self, db_user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = self.prepare_password(
                update_data.pop("password")
            )

        db_user.sqlmodel_update(update_data)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def delete(self, db_user: User) -> User:
        self.session.delete(db_user)
        self.session.commit()
        return db_user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        db_user = self.get_by_email(email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user

    def change_password(
        self, db_user: User, current_password: str, new_password: str
    ) -> User:
        if not verify_password(current_password, db_user.hashed_password):
            raise ValueError("La contraseña actual es incorrecta")
        db_user.hashed_password = get_password_hash(new_password)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def exists(self, user_id: UUID) -> bool:
        return self.session.get(User, user_id) is not None

    def count(self) -> int:
        """Cuenta el número total de usuarios en la base de datos."""
        stmt = select(func.count()).select_from(User)
        return self.session.exec(stmt).one()

    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = (
            select(User)
            .where(
                (User.email.ilike(f"%{search_term}%"))
                | (User.full_name.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def deactivate(self, db_user: User) -> User:
        db_user.is_active = False
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def activate(self, db_user: User) -> User:
        db_user.is_active = True
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
