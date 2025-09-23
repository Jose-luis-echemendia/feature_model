import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.common import Message
from app.enums import UserRole
from app.models.user import (
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


#######################################
## Endpoint para gestión de usuarios ##
#######################################


# ---------------------------------------------------------------------------
# Endpoint para leer la información de los usuarios.
# ---------------------------------------------------------------------------


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> UsersPublic:
    """
    Retrieve users.
    """
    users = crud.get_users(session=session, skip=skip, limit=limit)
    count = crud.get_users_count(session=session)
    
    return UsersPublic(data=users, count=count)


# ---------------------------------------------------------------------------
# Endpoint para obtener los usuarios dado un rol.
# ---------------------------------------------------------------------------


@router.get("/by-role/{role}", response_model=UsersPublic)
def read_users_by_role(session: SessionDep, role: UserRole, skip: int = 0, limit: int = 100) -> UsersPublic:
    """
    Get users by role.
    """
    # Para este caso específico, necesitamos una función especial en el CRUD
    # Podemos usar la función search_users o crear una específica
    statement = select(User).where(User.role == role).offset(skip).limit(limit)
    users = session.exec(statement).all()
    
    count_statement = select(func.count()).select_from(User).where(User.role == role)
    count = session.exec(count_statement).one()
    
    return UsersPublic(data=users, count=count)


# ---------------------------------------------------------------------------
# Endpoint para crear nuevos usuarios.
# ---------------------------------------------------------------------------


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> UserPublic:
    """
    Create new user.
    """
    try:
        user = crud.create_user(session=session, user_create=user_in)
        
        if settings.emails_enabled and user_in.email:
            email_data = generate_new_account_email(
                email_to=user_in.email, username=user_in.email, password=user_in.password
            )
            send_email(
                email_to=user_in.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ---------------------------------------------------------------------------
# Endpoint para actualizar el usuario propio.
# ---------------------------------------------------------------------------


@router.patch("/me/", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> UserPublic:
    """
    Update own user.
    """
    try:
        # Convertir UserUpdateMe a UserUpdate para usar la función del CRUD
        user_update_data = UserUpdate(**user_in.model_dump(exclude_unset=True))
        updated_user = crud.update_user(
            session=session, 
            db_user=current_user, 
            user_in=user_update_data
        )
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )


# ---------------------------------------------------------------------------
# Endpoint para cambiar la contraseña del usuario propio.
# ---------------------------------------------------------------------------


@router.patch("/me/password/", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Message:
    """
    Update own password.
    """
    try:
        updated_user = crud.change_password(
            session=session,
            db_user=current_user,
            current_password=body.current_password,
            new_password=body.new_password
        )
        return Message(message="Password updated successfully")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Endpoint para leer la información del usuario propio.
# ---------------------------------------------------------------------------


@router.get("/me/", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> UserPublic:
    """
    Get current user.
    """
    return current_user


# ---------------------------------------------------------------------------
# Endpoint para eliminar el usuario propio.
# ---------------------------------------------------------------------------


@router.delete("/me/", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Message:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    
    crud.delete_user(session=session, db_user=current_user)
    return Message(message="User deleted successfully")


# ---------------------------------------------------------------------------
# Endpoint para registrar un nuevo usuario.
# ---------------------------------------------------------------------------


@router.post("/signup/", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> UserPublic:
    """
    Create new user without the need to be logged in.
    """
    try:
        # Convertir UserRegister a UserCreate
        user_create = UserCreate(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
            # Agregar otros campos necesarios
        )
        user = crud.create_user(session=session, user_create=user_create)
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ---------------------------------------------------------------------------
# Endpoint para leer la información de los usuarios dado su id.
# ---------------------------------------------------------------------------


@router.get("/{user_id}/", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> UserPublic:
    """
    Get a specific user by id.
    """
    user = crud.get_user(session=session, user_id=user_id)
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


# ---------------------------------------------------------------------------
# Endpoint para actualizar un usuario dado su id.
# ---------------------------------------------------------------------------


@router.patch(
    "/{user_id}/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
    """
    Update a user.
    """
    db_user = crud.get_user(session=session, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    try:
        updated_user = crud.update_user(
            session=session, 
            db_user=db_user, 
            user_in=user_in
        )
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=409, 
            detail=str(e)
        )


# ---------------------------------------------------------------------------
# Endpoint para actualizar el rol de un usuario dado su id.
# ---------------------------------------------------------------------------


@router.put("/{user_id}/role/", response_model=UserPublic)
def update_user_role(
    user_id: uuid.UUID, 
    role: UserRole, 
    session: SessionDep,
    current_user: CurrentUser
) -> UserPublic:
    """
    Update a user's role.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    
    user = crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizar el rol usando la función del CRUD
    user_update = UserUpdate(role=role)
    updated_user = crud.update_user(
        session=session, 
        db_user=user, 
        user_in=user_update
    )
    return updated_user


# ---------------------------------------------------------------------------
# Endpoint para eliminar un usuario dado su id.
# ---------------------------------------------------------------------------


@router.delete("/{user_id}/", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    
    crud.delete_user(session=session, db_user=user)
    return Message(message="User deleted successfully")


# ---------------------------------------------------------------------------
# Endpoint adicional para buscar usuarios
# ---------------------------------------------------------------------------


@router.get("/search/{search_term}/", response_model=UsersPublic)
def search_users(
    session: SessionDep, 
    search_term: str, 
    skip: int = 0, 
    limit: int = 100
) -> UsersPublic:
    """
    Search users by email or name.
    """
    users = crud.search_users(
        session=session, 
        search_term=search_term, 
        skip=skip, 
        limit=limit
    )
    
    # Para el count, necesitamos una función específica o podemos contar los resultados
    count = len(users)
    
    return UsersPublic(data=users, count=count)


# ---------------------------------------------------------------------------
# Endpoint para activar/desactivar usuarios
# ---------------------------------------------------------------------------


@router.patch("/{user_id}/activate/", response_model=UserPublic)
def activate_user(
    user_id: uuid.UUID, 
    session: SessionDep, 
    current_user: CurrentUser
) -> UserPublic:
    """
    Activate a user.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    user = crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    activated_user = crud.activate_user(session=session, db_user=user)
    return activated_user


@router.patch("/{user_id}/deactivate/", response_model=UserPublic)
def deactivate_user(
    user_id: uuid.UUID, 
    session: SessionDep, 
    current_user: CurrentUser
) -> UserPublic:
    """
    Deactivate a user.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    
    user = crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user == current_user:
        raise HTTPException(status_code=403, detail="Cannot deactivate yourself")
    
    deactivated_user = crud.deactivate_user(session=session, db_user=user)
    return deactivated_user