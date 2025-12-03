import uuid

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
    users = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()

    # Calcular la página actual (asumiendo que skip/limit es la paginación)
    page = (skip // limit) + 1 if limit > 0 else 1
    size = len(users)

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
    users = await repo.search(role, skip=skip, limit=limit)
    total = len(users)

    # Calcular la página actual
    page = (skip // limit) + 1 if limit > 0 else 1
    size = len(users)

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
    if user_in.role == UserRole.DEVELOPER:
        # Solo desarrolladores pueden crear otros desarrolladores
        if current_user.role != UserRole.DEVELOPER:
            raise HTTPException(
                status_code=403,
                detail="Solo usuarios con rol DEVELOPER pueden crear otros desarrolladores",
            )
    elif not current_user.is_superuser:
        # Si no es superuser (admin o developer), no puede crear usuarios
        raise HTTPException(
            status_code=403, detail="No tienes permisos suficientes para crear usuarios"
        )

    try:
        user = await repo.create(user_in)

        if settings.emails_enabled and user_in.email:
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
    try:
        user_update_data = UserUpdate(**user_in.model_dump(exclude_unset=True))
        updated_user = await repo.update(db_user=current_user, data=user_update_data)
        return updated_user

    except ValueError as e:
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
    try:
        await repo.change_password(
            db_user=current_user,
            current_password=body.current_password,
            new_password=body.new_password,
        )
        return Message(message="Password updated successfully")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================================
#       --- Endpoint para leer la información del usuario propio ---
# ===========================================================================


@router.get("/me/", response_model=UserPublic)
async def read_user_me(*, current_user: CurrentUser) -> UserPublic:
    """
    Get current user.
    """
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
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    await repo.delete(db_user=current_user)
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
    allows_user_registration = await settings_service.aget(
        "ALLOWS_USER_REGISTRATION", default=False
    )

    if not allows_user_registration:
        return {"message": "El registro de usuarios está deshabilitado."}

    try:
        user_create = UserCreate(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
        )
        user = await repo.create(data=user_create)
        return user

    except ValueError as e:
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
    user = await repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        return user

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
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
    db_user = await repo.get(user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    try:
        updated_user = await repo.update(db_user=db_user, data=user_in)
        return updated_user

    except ValueError as e:
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
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )

    user = await repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_update = UserUpdate(role=role)
    updated_user = await repo.update(db_user=user, data=user_update)
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
    user = await repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    await repo.delete(db_user=user)
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
    users = await repo.search(search_term=search_term, skip=skip, limit=limit)
    total = len(users)

    # Calcular la página actual
    page = (skip // limit) + 1 if limit > 0 else 1
    size = len(users)

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
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    user = await repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    activated_user = await repo.activate(db_user=user)
    return activated_user


@router.patch("/{user_id}/deactivate/", response_model=UserPublic)
async def deactivate_user(
    *, user_id: uuid.UUID, repo: AsyncUserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Deactivate a user (async).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    user = await repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        raise HTTPException(status_code=403, detail="Cannot deactivate yourself")

    deactivated_user = await repo.deactivate(db_user=user)
    return deactivated_user
