import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    get_settings_service,
    get_current_active_superuser,
    CurrentUser,
    AsyncUserRepoDep,
)
from app.services import SettingsService
from app.core.config import settings
from app.models.common import Message
from app.enums import UserRole
from app.models.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UserListResponse,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import send_email

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


#######################################
## Endpoint para gestión de usuarios ##
#######################################


# ===========================================================================
#           --- Endpoint para listar Usuarios ---
# ===========================================================================


@router.get(
    "/",
    response_model=UserListResponse,
)
async def read_users(
    *,
    repo: AsyncUserRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    logger.info(f"📋 Listando usuarios - skip: {skip}, limit: {limit}")

    
    users = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    # Calcular la página actual (asumiendo que skip/limit es la paginación)
    page = (skip // limit) + 1 if limit > 0 else 1
    size = len(users)

    logger.info(f"✅ Usuarios obtenidos: {size} de {total} total")
    return UserListResponse(data=users, total=total, page=page, size=size)


# ===========================================================================
#           --- Endpoint para listar Usuarios por roles ---
# ===========================================================================


@router.get("/by-role/{role}", response_model=UserListResponse)
async def read_users_by_role(
    *,
    repo: AsyncUserRepoDep,
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    logger.info(f"🔍 Buscando usuarios por rol: {role.value} - skip: {skip}, limit: {limit}")
    
    users = await repo.search(role, skip=skip, limit=limit)
    total = len(users)

    # Calcular la página actual
    page = (skip // limit) + 1 if limit > 0 else 1
    size = len(users)

    logger.info(f"✅ Encontrados {total} usuarios con rol {role.value}")
    return UserListResponse(data=users, total=total, page=page, size=size)


# ===========================================================================
#           --- Endpoint para crear Usuario ---
# ===========================================================================


@router.post("/", response_model=UserPublic)
async def create_user(
    *,
    repo: AsyncUserRepoDep,
    current_user: CurrentUser,
    user_in: UserCreate,
) -> UserPublic:
    """
    Crea un nuevo usuario (diseñadores de modelos, editores de modelos, configuradores, espectadores, críticos, administradores o desarrollador).

    **Permisos requeridos:**
    - Administradores pueden crear: diseñadores de modelos, editores de modelos, configuradores, espectadores, críticos  y administradores
    - Desarrolladores pueden crear: todos los roles, incluido desarrollador

    **Validaciones**:
    - Email único
    - Contraseña fuerte (mínimo 8 caracteres)
    - Rol válido
    - Solo desarrolladores pueden crear otros desarrolladores
    """
    logger.info(f"👤 Intento de creación de usuario - Email: {user_in.email}, Rol: {user_in.role.value} por {current_user.email}")
    
    if user_in.role == UserRole.DEVELOPER:
        # Solo desarrolladores pueden crear otros desarrolladores
        if current_user.role != UserRole.DEVELOPER:
            logger.warning(f"❌ Usuario {current_user.email} (rol: {current_user.role.value}) intentó crear un DEVELOPER")
            raise HTTPException(
                status_code=403,
                detail="Solo usuarios con rol DEVELOPER pueden crear otros desarrolladores",
            )
    elif not current_user.is_superuser:
        # Si no es superuser (admin o developer), no puede crear usuarios
        logger.warning(f"❌ Usuario {current_user.email} sin permisos intentó crear usuario")
        raise HTTPException(
            status_code=403, detail="No tienes permisos suficientes para crear usuarios"
        )

    try:
        user = await repo.create(user_in)
        logger.info(f"✅ Usuario creado exitosamente: {user.email} con rol {user.role.value}")

        if settings.emails_enabled and user_in.email:
            logger.info(f"📧 Enviando email de bienvenida a: {user_in.email}")
            # usando thread pool si send_email es sync
            import anyio

            await anyio.to_thread.run_sync(
                send_email,
                user_in.email,
                "Bienvenido",
                "<p>Cuenta creada</p>",
            )

        return user

    except ValueError as e:
        logger.error(f"❌ Error al crear usuario {user_in.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================================
#           --- Endpoint para actualizar el usuario propio ---
# ===========================================================================


@router.patch("/me/", response_model=UserPublic)
async def update_user_me_(
    *, repo: AsyncUserRepoDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> UserPublic:
    """
    Update own user (async).
    """
    logger.info(f"👤 Usuario {current_user.email} actualizando su propio perfil")
    
    try:
        user_update_data = UserUpdate(**user_in.model_dump(exclude_unset=True))
        updated_user = await repo.update(db_user=current_user, data=user_update_data)
        logger.info(f"✅ Perfil actualizado exitosamente para: {current_user.email}")
        return updated_user

    except ValueError as e:
        logger.error(f"❌ Error al actualizar perfil de {current_user.email}: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))


# ===========================================================================
#        --- Endpoint para cambiar la contraseña del usuario propio ---
# ===========================================================================


@router.patch("/me/password/", response_model=Message)
async def update_password_me(
    *, repo: AsyncUserRepoDep, body: UpdatePassword, current_user: CurrentUser
) -> Message:
    """
    Update own password (async).
    """
    logger.info(f"🔑 Usuario {current_user.email} cambiando su contraseña")
    
    try:
        await repo.change_password(
            db_user=current_user,
            current_password=body.current_password,
            new_password=body.new_password,
        )
        logger.info(f"✅ Contraseña actualizada exitosamente para: {current_user.email}")
        return Message(message="Password updated successfully")

    except ValueError as e:
        logger.warning(f"❌ Error al cambiar contraseña para {current_user.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================================
#       --- Endpoint para leer la información del usuario propio ---
# ===========================================================================


@router.get("/me/", response_model=UserPublic)
async def read_user_me(*, current_user: CurrentUser) -> UserPublic:
    """
    Get current user.
    """
    logger.info(f"👤 Usuario {current_user.email} consultando su propio perfil")
    return current_user


# ===========================================================================
#       --- Endpoint para eliminar el usuario propio ---
# ===========================================================================


@router.delete("/me/", response_model=Message)
async def delete_user_me(
    *, repo: AsyncUserRepoDep, current_user: CurrentUser
) -> Message:
    """
    Delete own user (async).
    """
    logger.info(f"🗑️ Usuario {current_user.email} solicitando eliminar su propia cuenta")
    
    if current_user.is_superuser:
        logger.warning(f"❌ Superusuario {current_user.email} intentó auto-eliminarse")
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    await repo.delete(db_user=current_user)
    logger.info(f"✅ Cuenta eliminada exitosamente: {current_user.email}")
    return Message(message="User deleted successfully")


# ===========================================================================
#           --- Endpoint para registrar un nuevo usuario ---
# ===========================================================================


@router.post("/signup/", response_model=UserPublic)
async def register_user(
    *,
    repo: AsyncUserRepoDep,
    user_in: UserRegister,
    settings_service: SettingsService = Depends(get_settings_service),
) -> UserPublic:
    """
    Create new user without the need to be logged in (async).
    """
    logger.info(f"📝 Intento de registro de nuevo usuario: {user_in.email}")
    
    allows_user_registration = await settings_service.aget(
        "ALLOWS_USER_REGISTRATION", default=False
    )

    if not allows_user_registration:
        logger.warning(f"❌ Registro bloqueado - función deshabilitada para: {user_in.email}")
        return {"message": "El registro de usuarios está deshabilitado."}

    try:
        user_create = UserCreate(
            email=user_in.email,
            password=user_in.password,
        )
        user = await repo.create(data=user_create)
        logger.info(f"✅ Usuario registrado exitosamente: {user.email}")
        return user

    except ValueError as e:
        logger.error(f"❌ Error al registrar usuario {user_in.email}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ===========================================================================
#     --- Endpoint para leer la información de los usuarios dado su id ---
# ===========================================================================


@router.get("/{user_id}/", response_model=UserPublic)
async def read_user_by_id(
    *, user_id: uuid.UUID, repo: AsyncUserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Get a specific user by id (async).
    """
    logger.info(f"🔍 Usuario {current_user.email} consultando información de user_id: {user_id}")
    
    user = await repo.get(user_id=user_id)
    if not user:
        logger.warning(f"❌ Usuario no encontrado - ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        logger.info(f"✅ Usuario consultando su propia información: {current_user.email}")
        return user

    if not current_user.is_superuser:
        logger.warning(f"❌ Usuario {current_user.email} sin permisos para ver información de {user.email}")
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    
    logger.info(f"✅ Información de usuario {user.email} entregada a superusuario {current_user.email}")
    return user


# ===========================================================================
#       --- Endpoint para actualizar un usuario dado su id ---
# ===========================================================================


@router.patch(
    "/{user_id}/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    *,
    repo: AsyncUserRepoDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
    """
    Update a user (async).
    """
    logger.info(f"👤 Superusuario actualizando usuario ID: {user_id}")
    
    db_user = await repo.get(user_id=user_id)
    if not db_user:
        logger.warning(f"❌ Usuario no encontrado para actualizar - ID: {user_id}")
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    try:
        updated_user = await repo.update(db_user=db_user, data=user_in)
        logger.info(f"✅ Usuario {db_user.email} actualizado exitosamente")
        return updated_user

    except ValueError as e:
        logger.error(f"❌ Error al actualizar usuario {db_user.email}: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))


# ===========================================================================
#       --- Endpoint para actualizar el rol de un usuario dado su id ---
# ===========================================================================


@router.put("/{user_id}/role/", response_model=UserPublic)
async def update_user_role(
    *,
    user_id: uuid.UUID,
    role: UserRole,
    repo: AsyncUserRepoDep,
    current_user: CurrentUser,
) -> UserPublic:
    """
    Update a user's role (async).
    """
    logger.info(f"🔐 Usuario {current_user.email} intentando cambiar rol de user_id {user_id} a {role.value}")
    
    if not current_user.is_superuser:
        logger.warning(f"❌ Usuario {current_user.email} sin permisos para cambiar roles")
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )

    user = await repo.get(user_id=user_id)
    if not user:
        logger.warning(f"❌ Usuario no encontrado para cambio de rol - ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"🔄 Cambiando rol de {user.email} de {user.role.value} a {role.value}")
    user_update = UserUpdate(role=role)
    updated_user = await repo.update(db_user=user, data=user_update)
    logger.info(f"✅ Rol actualizado exitosamente para {user.email}")
    return updated_user


# ===========================================================================
#       --- Endpoint para eliminar un usuario dado su id ---
# ===========================================================================


@router.delete("/{user_id}/", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(
    *, repo: AsyncUserRepoDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user (async).
    """
    logger.info(f"🗑️ Superusuario {current_user.email} solicitando eliminar usuario ID: {user_id}")
    
    user = await repo.get(user_id=user_id)
    if not user:
        logger.warning(f"❌ Usuario no encontrado para eliminar - ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        logger.warning(f"❌ Superusuario {current_user.email} intentó auto-eliminarse")
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    logger.info(f"🗑️ Eliminando usuario: {user.email}")
    await repo.delete(db_user=user)
    logger.info(f"✅ Usuario {user.email} eliminado exitosamente")
    return Message(message="User deleted successfully")


# ===========================================================================
#           --- Endpoint adicional para buscar usuarios ---
# ===========================================================================


@router.get("/search/{search_term}/", response_model=UserListResponse)
async def search_users(
    *, repo: AsyncUserRepoDep, search_term: str, skip: int = 0, limit: int = 100
) -> UserListResponse:
    """
    Search users by email or name (async).
    """
    logger.info(f"🔍 Búsqueda de usuarios con término: '{search_term}' - skip: {skip}, limit: {limit}")
    
    users = await repo.search(search_term=search_term, skip=skip, limit=limit)
    total = len(users)

    # Calcular la página actual
    page = (skip // limit) + 1 if limit > 0 else 1
    size = len(users)

    logger.info(f"✅ Búsqueda completada: {size} usuarios encontrados")
    return UserListResponse(data=users, total=total, page=page, size=size)


# ===========================================================================
#       --- Endpoint para activar/desactivar usuarios ---
# ===========================================================================


@router.patch("/{user_id}/activate/", response_model=UserPublic)
async def activate_user(
    *, user_id: uuid.UUID, repo: AsyncUserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Activate a user (async).
    """
    logger.info(f"🔓 Superusuario {current_user.email} activando usuario ID: {user_id}")
    
    if not current_user.is_superuser:
        logger.warning(f"❌ Usuario {current_user.email} sin permisos para activar usuarios")
        raise HTTPException(status_code=403, detail="Not enough privileges")

    user = await repo.get(user_id=user_id)
    if not user:
        logger.warning(f"❌ Usuario no encontrado para activar - ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    activated_user = await repo.activate(db_user=user)
    logger.info(f"✅ Usuario {user.email} activado exitosamente")
    return activated_user


@router.patch("/{user_id}/deactivate/", response_model=UserPublic)
async def deactivate_user(
    *, user_id: uuid.UUID, repo: AsyncUserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Deactivate a user (async).
    """
    logger.info(f"🔒 Superusuario {current_user.email} desactivando usuario ID: {user_id}")
    
    if not current_user.is_superuser:
        logger.warning(f"❌ Usuario {current_user.email} sin permisos para desactivar usuarios")
        raise HTTPException(status_code=403, detail="Not enough privileges")

    user = await repo.get(user_id=user_id)
    if not user:
        logger.warning(f"❌ Usuario no encontrado para desactivar - ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        logger.warning(f"❌ Superusuario {current_user.email} intentó auto-desactivarse")
        raise HTTPException(status_code=403, detail="Cannot deactivate yourself")

    deactivated_user = await repo.deactivate(db_user=user)
    logger.info(f"✅ Usuario {user.email} desactivado exitosamente")
    return deactivated_user
