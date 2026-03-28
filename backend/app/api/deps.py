from typing import Annotated, AsyncGenerator, Awaitable, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.common import TokenPayload
from app.models.user import User
from app.enums import UserRole
from app.core import security

from app.core.config import settings
from app.core.db import a_engine


# ========================================================================
#     --- DEPENDENCIAS PARA OAUTH2 ---
# ========================================================================

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/login/access-token",
    auto_error=False,  # Permite manejar tokens opcionales
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]
OptionalTokenDep = Annotated[str | None, Depends(reusable_oauth2)]


# ========================================================================
#     --- DEPENDENCIAS PARA OBTENER LA SESSION DE LA BD ---
# ========================================================================

# --- DEPENDENCIAS PARA ASYNC SESSION ---

SessionLocal = async_sessionmaker(
    bind=a_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def a_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(a_get_db)]


# ========================================================================
#     --- DEPENDENCIAS PARA LOS REPOSITORIOS ---
# ========================================================================

from app.repositories import (
    UserRepository,
    DomainRepository,
    FeatureModelRepository,
    FeatureRepository,
    FeatureRelationRepository,
    FeatureGroupRepository,
    ConstraintRepository,
    ConfigurationRepository,
    FeatureModelVersionRepository,
)


async def get_user_repo(session: SessionDep):
    return UserRepository(session)


async def get_domain_repo(session: SessionDep):
    return DomainRepository(session)


async def get_feature_model_repo(session: SessionDep):
    return FeatureModelRepository(session)


async def get_feature_repo(session: SessionDep):
    return FeatureRepository(session)


async def get_feature_relation_repo(session: SessionDep):
    return FeatureRelationRepository(session)


async def get_feature_group_repo(session: SessionDep):
    return FeatureGroupRepository(session)


async def get_constraint_repo(session: SessionDep):
    return ConstraintRepository(session)


async def get_configuration_repo(session: SessionDep):
    return ConfigurationRepository(session)


async def get_feature_model_version_repo(session: SessionDep):
    return FeatureModelVersionRepository(session)


# usuarios
AsyncUserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
# dominios
AsyncDomainRepoDep = Annotated[DomainRepository, Depends(get_domain_repo)]
# feature models
AsyncFeatureModelRepoDep = Annotated[
    FeatureModelRepository, Depends(get_feature_model_repo)
]
# feature
AsyncFeatureRepoDep = Annotated[FeatureRepository, Depends(get_feature_repo)]
# feature relation
AsyncFeatureRelationRepoDep = Annotated[
    FeatureRelationRepository, Depends(get_feature_relation_repo)
]
# feature group
AsyncFeatureGroupRepoDep = Annotated[
    FeatureGroupRepository, Depends(get_feature_group_repo)
]
# constraint
AsyncConstraintRepoDep = Annotated[ConstraintRepository, Depends(get_constraint_repo)]
# configuration
AsyncConfigurationRepoDep = Annotated[
    ConfigurationRepository, Depends(get_configuration_repo)
]
# feature model version
AsyncFeatureModelVersionRepoDep = Annotated[
    FeatureModelVersionRepository, Depends(get_feature_model_version_repo)
]


# ========================================================================
#     --- DEPENDENCIAS ASÍNCRONAS PARA USUARIOS AUTENTICADOS ---
# ========================================================================


async def get_current_user(user_repo: AsyncUserRepoDep, token: TokenDep) -> User:
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
            settings.SECRET_KEY.get_secret_value(),
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


async def get_optional_user(
    user_repo: AsyncUserRepoDep, token: OptionalTokenDep = None
) -> User | None:
    """
    Obtener usuario actual si existe token, sino retornar None (versión asíncrona).
    Útil para endpoints que funcionan tanto para usuarios autenticados como anónimos.
    """
    if not token:
        return None

    try:
        return await get_current_user(user_repo=user_repo, token=token)
    except HTTPException:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]

# Alias de compatibilidad
AsyncCurrentUser = CurrentUser
AsyncOptionalUser = OptionalUser


# ========================================================================
#     --- DEPENDENCIAS PARA SUPER USUARIOS ---
# ========================================================================


async def get_current_active_superuser(current_user: CurrentUser) -> User:
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


def role_required(
    allowed_roles: list[UserRole],
) -> Callable[[CurrentUser], Awaitable[User]]:
    """
    Factory para crear dependencias de verificación de roles.

    Args:
        allowed_roles: Lista de roles permitidos

    Returns:
        Callable: Dependencia que verifica los roles
    """

    async def dependency(current_user: CurrentUser) -> User:
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


async def get_developer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios desarrolladores (máximo nivel de acceso)."""
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


async def get_admin_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios administradores."""
    if current_user.role not in [UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


async def get_model_designer_user(current_user: CurrentUser) -> User:
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


async def get_editor_user(current_user: CurrentUser) -> User:
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


async def get_configurator_user(current_user: CurrentUser) -> User:
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


async def get_viewer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios observadores"""
    if current_user.role not in [UserRole.VIEWER, UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: VIEWER, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


async def get_reviewer_user(current_user: CurrentUser) -> User:
    """Dependencia para usuarios revisores"""
    if current_user.role not in [UserRole.REVIEWER, UserRole.ADMIN, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: REVIEWER, ADMIN or DEVELOPER. Current role: {current_user.role.value}",
        )
    return current_user


async def get_verified_user(current_user: CurrentUser) -> User:
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


async def get_settings_service(session: SessionDep) -> SettingsService:
    return SettingsService(session=session)


SettingsServiceDep = Annotated[SettingsService, Depends(get_settings_service)]
