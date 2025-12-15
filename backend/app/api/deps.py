from collections.abc import Generator
from typing import Annotated, Callable, AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import ValidationError
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.common import TokenPayload
from app.models.user import User
from app.enums import UserRole
from app.core import security

from app.core.config import settings
from app.core.db import engine, a_engine


# ========================================================================
#     --- DEPENDENCIAS PARA OAUTH2 ---
# ========================================================================

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False,  # Permite manejar tokens opcionales
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]
OptionalTokenDep = Annotated[str | None, Depends(reusable_oauth2)]


# ========================================================================
#     --- DEPENDENCIAS PARA OBTENER LA SESSION DE LA BD ---
# ========================================================================

# --- DEPENDENCIAS PARA ASYNC SESSION ---

AsyncSessionLocal = async_sessionmaker(
    bind=a_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def a_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(a_get_db)]


# --- DEPENDENCIAS PARA SYNC SESSION ---


def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de base de datos."""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


SessionDep = Annotated[Session, Depends(get_db)]


# ========================================================================
#     --- DEPENDENCIAS PARA LOS REPOSITORIOS ---
# ========================================================================

from app.repositories import (
    UserRepositorySync,
    UserRepositoryAsync,
    DomainRepositorySync,
    DomainRepositoryAsync,
    FeatureModelRepositorySync,
    FeatureModelRepositoryAsync,
    FeatureRepositorySync,
    FeatureRepositoryAsync,
    FeatureRelationRepositorySync,
    FeatureRelationRepositoryAsync,
    FeatureGroupRepositorySync,
    FeatureGroupRepositoryAsync,
    ConstraintRepositorySync,
    ConstraintRepositoryAsync,
    ConfigurationRepositorySync,
    ConfigurationRepositoryAsync,
    FeatureModelVersionRepositorySync,
    FeatureModelVersionRepositoryAsync,
)


def get_user_repo(session: SessionDep):
    return UserRepositorySync(session)


async def aget_user_repo(session: AsyncSessionDep):
    return UserRepositoryAsync(session)


def get_domain_repo(session: SessionDep):
    return DomainRepositorySync(session)


async def aget_domain_repo(session: AsyncSessionDep):
    return DomainRepositoryAsync(session)


def get_feature_model_repo(session: SessionDep):
    return FeatureModelRepositorySync(session)


async def aget_feature_model_repo(session: AsyncSessionDep):
    return FeatureModelRepositoryAsync(session)


def get_feature_repo(session: SessionDep):
    return FeatureRepositorySync(session)


async def aget_feature_repo(session: AsyncSessionDep):
    return FeatureRepositoryAsync(session)


def get_feature_relation_repo(session: SessionDep):
    return FeatureRelationRepositorySync(session)


async def aget_feature_relation_repo(session: AsyncSessionDep):
    return FeatureRelationRepositoryAsync(session)


def get_feature_group_repo(session: SessionDep):
    return FeatureGroupRepositorySync(session)


async def aget_feature_group_repo(session: AsyncSessionDep):
    return FeatureGroupRepositoryAsync(session)


def get_constraint_repo(session: SessionDep):
    return ConstraintRepositorySync(session)


async def aget_constraint_repo(session: AsyncSessionDep):
    return ConstraintRepositoryAsync(session)


def get_configuration_repo(session: SessionDep):
    return ConfigurationRepositorySync(session)


async def aget_configuration_repo(session: AsyncSessionDep):
    return ConfigurationRepositoryAsync(session)


def get_feature_model_version_repo(session: SessionDep):
    return FeatureModelVersionRepositorySync(session)


async def aget_feature_model_version_repo(session: AsyncSessionDep):
    return FeatureModelVersionRepositoryAsync(session)


# usuarios
UserRepoDep = Annotated[UserRepositorySync, Depends(get_user_repo)]
AsyncUserRepoDep = Annotated[UserRepositoryAsync, Depends(aget_user_repo)]
# dominios
DomainRepoDep = Annotated[DomainRepositorySync, Depends(get_domain_repo)]
AsyncDomainRepoDep = Annotated[DomainRepositoryAsync, Depends(aget_domain_repo)]
# feature models
FeatureModelRepoDep = Annotated[
    FeatureModelRepositorySync, Depends(get_feature_model_repo)
]
AsyncFeatureModelRepoDep = Annotated[
    FeatureModelRepositoryAsync, Depends(aget_feature_model_repo)
]
# feature
FeatureRepoDep = Annotated[FeatureRepositorySync, Depends(get_feature_repo)]
AsyncFeatureRepoDep = Annotated[FeatureRepositoryAsync, Depends(aget_feature_repo)]
# feature relation
FeatureRelationRepoDep = Annotated[
    FeatureRelationRepositorySync, Depends(get_feature_relation_repo)
]
AsyncFeatureRelationRepoDep = Annotated[
    FeatureRelationRepositoryAsync, Depends(aget_feature_relation_repo)
]
# feature group
FeatureGroupRepoDep = Annotated[
    FeatureGroupRepositorySync, Depends(get_feature_group_repo)
]
AsyncFeatureGroupRepoDep = Annotated[
    FeatureGroupRepositoryAsync, Depends(aget_feature_group_repo)
]
# constraint
ConstraintRepoDep = Annotated[ConstraintRepositorySync, Depends(get_constraint_repo)]
AsyncConstraintRepoDep = Annotated[
    ConstraintRepositoryAsync, Depends(aget_constraint_repo)
]
# configuration
ConfigurationRepoDep = Annotated[
    ConfigurationRepositorySync, Depends(get_configuration_repo)
]
AsyncConfigurationRepoDep = Annotated[
    ConfigurationRepositoryAsync, Depends(aget_configuration_repo)
]
# feature model version
FeatureModelVersionRepoDep = Annotated[
    FeatureModelVersionRepositorySync, Depends(get_feature_model_version_repo)
]
AsyncFeatureModelVersionRepoDep = Annotated[
    FeatureModelVersionRepositoryAsync, Depends(aget_feature_model_version_repo)
]


# ========================================================================
#     --- DEPENDENCIAS PARA USUARIOS AUTENTICADOS ---
# ========================================================================


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Obtener usuario actual basado en el token JWT.

    Args:
        session: Sesión de base de datos
        token: Token JWT

    Returns:
        User: Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido, expirado o el usuario no existe/inactivo
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            options={"verify_exp": True},  # Asegurar verificación de expiración
        )
        token_data = TokenPayload(**payload)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidTokenError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Usar el repositorio para obtener el usuario
    user_repo = UserRepositorySync(session)
    user = user_repo.get(user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def get_optional_user(
    session: SessionDep, token: OptionalTokenDep = None
) -> User | None:
    """
    Obtener usuario actual si existe token, sino retornar None.
    Útil para endpoints que funcionan tanto para usuarios autenticados como anónimos.
    """
    if not token:
        return None

    try:
        return get_current_user(token=token)
    except HTTPException:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]


# --- VERSIONES ASÍNCRONAS DE AUTENTICACIÓN ---


async def aget_current_user(user_repo: AsyncUserRepoDep, token: TokenDep) -> User:
    """
    Obtener usuario actual basado en el token JWT (versión asíncrona).

    Args:
        user_repo: Repositorio de usuarios asíncrono
        token: Token JWT

    Returns:
        User: Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido, expirado o el usuario no existe/inactivo
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            options={"verify_exp": True},
        )
        token_data = TokenPayload(**payload)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get(user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def aget_optional_user(
    user_repo: AsyncUserRepoDep, token: OptionalTokenDep = None
) -> User | None:
    """
    Obtener usuario actual si existe token, sino retornar None (versión asíncrona).
    Útil para endpoints que funcionan tanto para usuarios autenticados como anónimos.
    """
    if not token:
        return None

    try:
        return await aget_current_user(user_repo=user_repo, token=token)
    except HTTPException:
        return None


AsyncCurrentUser = Annotated[User, Depends(aget_current_user)]
AsyncOptionalUser = Annotated[User | None, Depends(aget_optional_user)]


# ========================================================================
#     --- DEPENDENCIAS PARA SUPER USUARIOS ---
# ========================================================================


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Verificar que el usuario actual sea superusuario activo.

    Args:
        current_user: Usuario actual

    Returns:
        User: Usuario superusuario

    Raises:
        HTTPException: Si el usuario no es superusuario
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]


# ========================================================================
#     --- DEPENDENCIAS PARA LOS ROLES DEL SISTEMA ---
# ========================================================================


def role_required(allowed_roles: list[UserRole]) -> Callable[[CurrentUser], User]:
    """
    Factory para crear dependencias de verificación de roles.

    Args:
        allowed_roles: Lista de roles permitidos

    Returns:
        Callable: Dependencia que verifica los roles
    """

    def dependency(current_user: CurrentUser) -> User:
        """
        Verificar si el usuario tiene uno de los roles permitidos.

        Args:
            current_user: Usuario actual

        Returns:
            User: Usuario si tiene los permisos

        Raises:
            HTTPException: Si el usuario no tiene los permisos requeridos
        """
        if current_user.role not in allowed_roles:
            allowed_roles_str = ", ".join([role.value for role in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"The user does not have the required permissions. "
                    f"Allowed roles: {allowed_roles_str}. "
                    f"Current role: {current_user.role.value}"
                ),
            )
        return current_user

    return dependency


# Dependencias predefinidas para roles comunes


def get_developer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios desarrolladores (máximo nivel de acceso)."""
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_admin_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios administradores."""
    if current_user.role not in [UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_model_designer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios diseñadores de modelos."""
    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: MODEL_DESIGNER, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_editor_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios editores"""
    if current_user.role not in [
        UserRole.MODEL_EDITOR,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: MODEL_EDITOR, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_configurator_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios configuradores"""
    if current_user.role not in [
        UserRole.CONFIGURATOR,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: CONFIGURATOR, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_viewer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios observadores"""
    if current_user.role not in [UserRole.VIEWER, UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: VIEWER, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_reviewer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios revisores"""
    if current_user.role not in [UserRole.REVIEWER, UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: REVIEWER, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


def get_verified_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios verificados (no guests)."""
    allowed_roles = [
        UserRole.DEVELOPER,
        UserRole.ADMIN,
        UserRole.MODEL_DESIGNER,
        UserRole.MODEL_EDITOR,
        UserRole.CONFIGURATOR,
        UserRole.VIEWER,
        UserRole.REVIEWER,
    ]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. User must have a verified role. Current role: {current_user.role.value}",
        )
    return current_user


# Atajos comunes
DeveloperUser = Annotated[User, Depends(get_developer_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]
ModelDesignerUser = Annotated[User, Depends(get_model_designer_user)]
ConfiguratorUser = Annotated[User, Depends(get_configurator_user)]
ViewerUser = Annotated[User, Depends(get_viewer_user)]
VerifiedUser = Annotated[User, Depends(get_verified_user)]


# ========================================================================
#     --- DEPENDENCIAS PARA LA GESTIÓN DE VARIABLES DE CONFIGURACIÓN ---
# ========================================================================

from app.services.settings import SettingsService


def get_settings_service(session: SessionDep) -> SettingsService:
    return SettingsService(session=session)


SettingsServiceDep = Annotated[SettingsService, Depends(get_settings_service)]
