import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    CurrentUser,
    get_current_active_superuser,
    UserRepoDep,
    AsyncUserRepoDep,
)
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
from app.utils import generate_new_account_email, send_email

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
def read_users(
    *,
    repo: UserRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    users = repo.get_all(skip=skip, limit=limit)
    count = repo.count()
    return UserListResponse(data=users, count=count)


@router.get(
    "/async",
    response_model=UserListResponse,
)
async def read_users_async(
    *,
    repo: AsyncUserRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    users = await repo.get_all(skip=skip, limit=limit)
    count = await repo.count()
    return UserListResponse(data=users, count=count)


# ===========================================================================
#           --- Endpoint para listar Usuarios por roles ---
# ===========================================================================

@router.get("/async/by-role/{role}", response_model=UserListResponse)
async def read_users_by_role_async(
    *,
    repo: AsyncUserRepoDep,
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    users = await repo.search(role, skip=skip, limit=limit)
    count = len(users)
    return UserListResponse(data=users, count=count)


@router.get("/by-role/{role}", response_model=UserListResponse)
def read_users_by_role(
    *,
    repo: UserRepoDep,
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    users = repo.search(role, skip=skip, limit=limit)
    count = len(users)  # o repo.count_by_role(role) si existe
    return UserListResponse(data=users, count=count)



# ===========================================================================
#           --- Endpoint para crear Usuario ---
# ===========================================================================

@router.post("/", response_model=UserPublic)
def create_user(
    *,
    repo: UserRepoDep,
    user_in: UserCreate,
) -> UserPublic:
    try:
        user = repo.create(user_in)

        # Lógica de email se mantiene igual
        if settings.emails_enabled and user_in.email:
            email_data = generate_new_account_email(
                email_to=user_in.email,
                username=user_in.email,
                password=user_in.password,
            )
            send_email(
                email_to=user_in.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

        return user

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/async", response_model=UserPublic)
async def create_user_async(
    *,
    repo: AsyncUserRepoDep,
    user_in: UserCreate,
) -> UserPublic:
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
def update_user_me(
    *, repo: UserRepoDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> UserPublic:
    """
    Update own user.
    """
    try:
        # Convertir UserUpdateMe a UserUpdate para usar el repositorio
        user_update_data = UserUpdate(**user_in.model_dump(exclude_unset=True))
        updated_user = repo.update(db_user=current_user, data=user_update_data)
        return updated_user

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/me/async", response_model=UserPublic)
async def update_user_me_async(
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
def update_password_me(
    *, repo: UserRepoDep, body: UpdatePassword, current_user: CurrentUser
) -> Message:
    """
    Update own password.
    """
    try:
        repo.change_password(
            db_user=current_user,
            current_password=body.current_password,
            new_password=body.new_password,
        )
        return Message(message="Password updated successfully")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/me/password/async", response_model=Message)
async def update_password_me_async(
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
def read_user_me(*, current_user: CurrentUser) -> UserPublic:
    """
    Get current user.
    """
    return current_user


# ===========================================================================
#       --- Endpoint para eliminar el usuario propio ---
# ===========================================================================


@router.delete("/me/", response_model=Message)
def delete_user_me(*, repo: UserRepoDep, current_user: CurrentUser) -> Message:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    repo.delete(db_user=current_user)
    return Message(message="User deleted successfully")


@router.delete("/me/async", response_model=Message)
async def delete_user_me_async(
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
def register_user(*, repo: UserRepoDep, user_in: UserRegister) -> UserPublic:
    """
    Create new user without the need to be logged in.
    """
    try:
        # Convertir UserRegister a UserCreate
        user_create = UserCreate(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
        )
        user = repo.create(data=user_create)
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post("/signup/async", response_model=UserPublic)
async def register_user_async(
    *, repo: AsyncUserRepoDep, user_in: UserRegister
) -> UserPublic:
    """
    Create new user without the need to be logged in (async).
    """
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
def read_user_by_id(
    *, user_id: uuid.UUID, repo: UserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Get a specific user by id.
    """
    user = repo.get(user_id=user_id)
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


@router.get("/{user_id}/async", response_model=UserPublic)
async def read_user_by_id_async(
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
def update_user(
    *,
    repo: UserRepoDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
    """
    Update a user.
    """
    db_user = repo.get(user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    try:
        updated_user = repo.update(db_user=db_user, data=user_in)
        return updated_user

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch(
    "/{user_id}/async",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user_async(
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
def update_user_role(
    *,
    user_id: uuid.UUID,
    role: UserRole,
    repo: UserRepoDep,
    current_user: CurrentUser,
) -> UserPublic:
    """
    Update a user's role.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )

    user = repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizar el rol usando el repositorio
    user_update = UserUpdate(role=role)
    updated_user = repo.update(db_user=user, data=user_update)
    return updated_user


@router.put("/{user_id}/role/async", response_model=UserPublic)
async def update_user_role_async(
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
def delete_user(
    *, repo: UserRepoDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    repo.delete(db_user=user)
    return Message(message="User deleted successfully")


@router.delete("/{user_id}/async", dependencies=[Depends(get_current_active_superuser)])
async def delete_user_async(
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
def search_users(
    *, repo: UserRepoDep, search_term: str, skip: int = 0, limit: int = 100
) -> UserListResponse:
    """
    Search users by email or name.
    """
    users = repo.search(search_term=search_term, skip=skip, limit=limit)
    count = len(users)
    return UserListResponse(data=users, count=count)


@router.get("/search/{search_term}/async", response_model=UserListResponse)
async def search_users_async(
    *, repo: AsyncUserRepoDep, search_term: str, skip: int = 0, limit: int = 100
) -> UserListResponse:
    """
    Search users by email or name (async).
    """
    users = await repo.search(search_term=search_term, skip=skip, limit=limit)
    count = len(users)
    return UserListResponse(data=users, count=count)


# ===========================================================================
#       --- Endpoint para activar/desactivar usuarios ---
# ===========================================================================


@router.patch("/{user_id}/activate/", response_model=UserPublic)
def activate_user(
    *, user_id: uuid.UUID, repo: UserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Activate a user.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    user = repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    activated_user = repo.activate(db_user=user)
    return activated_user


@router.patch("/{user_id}/activate/async", response_model=UserPublic)
async def activate_user_async(
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
def deactivate_user(
    *, user_id: uuid.UUID, repo: UserRepoDep, current_user: CurrentUser
) -> UserPublic:
    """
    Deactivate a user.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    user = repo.get(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        raise HTTPException(status_code=403, detail="Cannot deactivate yourself")

    deactivated_user = repo.deactivate(db_user=user)
    return deactivated_user


@router.patch("/{user_id}/deactivate/async", response_model=UserPublic)
async def deactivate_user_async(
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
