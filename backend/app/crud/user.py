from uuid import UUID
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Crear un nuevo usuario"""
    # Verificar si ya existe un usuario con el mismo email
    existing_user = get_user_by_email(session=session, email=user_create.email)
    if existing_user:
        raise ValueError(f"Ya existe un usuario con el email: {user_create.email}")
    
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user(*, session: Session, user_id: UUID) -> User | None:
    """Obtener un usuario por ID"""
    return session.get(User, user_id)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Obtener un usuario por email"""
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Obtener lista de usuarios con paginación"""
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Actualizar un usuario existente"""
    user_data = user_in.model_dump(exclude_unset=True)
    
    # Si se está actualizando el email, verificar que no exista otro con el mismo email
    if "email" in user_data and user_data["email"] != db_user.email:
        existing_user = get_user_by_email(session=session, email=user_data["email"])
        if existing_user and existing_user.id != db_user.id:
            raise ValueError(f"Ya existe otro usuario con el email: {user_data['email']}")
    
    # Manejar actualización de contraseña
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
        # Remover password del diccionario principal para evitar conflictos
        user_data.pop("password")
    
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(*, session: Session, db_user: User) -> User:
    """Eliminar un usuario"""
    session.delete(db_user)
    session.commit()
    return db_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Autenticar usuario con email y contraseña"""
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def change_password(*, session: Session, db_user: User, current_password: str, new_password: str) -> User:
    """Cambiar contraseña del usuario con verificación de contraseña actual"""
    if not verify_password(current_password, db_user.hashed_password):
        raise ValueError("La contraseña actual es incorrecta")
    
    db_user.hashed_password = get_password_hash(new_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def user_exists(*, session: Session, user_id: UUID) -> bool:
    """Verificar si un usuario existe"""
    return session.get(User, user_id) is not None


def get_users_count(*, session: Session) -> int:
    """Obtener el número total de usuarios"""
    statement = select(User)
    return len(session.exec(statement).all())


def search_users(*, session: Session, search_term: str, skip: int = 0, limit: int = 100) -> list[User]:
    """Buscar usuarios por email o nombre"""
    statement = select(User).where(
        (User.email.ilike(f"%{search_term}%"))
    ).offset(skip).limit(limit)
    return session.exec(statement).all()


def deactivate_user(*, session: Session, db_user: User) -> User:
    """Desactivar un usuario (soft delete)"""
    db_user.is_active = False
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def activate_user(*, session: Session, db_user: User) -> User:
    """Activar un usuario previamente desactivado"""
    db_user.is_active = True
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user