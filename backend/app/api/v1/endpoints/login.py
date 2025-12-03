from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.api.deps import (
    AsyncCurrentUser,
    AsyncSessionDep,
    AsyncUserRepoDep,
    get_current_active_superuser,
)
from app.models import Message, NewPassword, Token, LoginRequest, UserPublic
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token/")
async def login_access_token(
    *, user_repo: AsyncUserRepoDep, login_data: LoginRequest
) -> Token:
    """
    ## Login de usuario con email y contraseña

    Endpoint compatible con OAuth2 para obtener un token de acceso JWT.

    ### Parámetros
    - **email**: Email del usuario registrado
    - **password**: Contraseña del usuario

    ### Retorna
    - **access_token**: Token JWT para autenticación en futuras peticiones
    - **token_type**: Tipo de token (siempre "bearer")

    ### Errores
    - **400**: Email o contraseña incorrectos
    - **400**: Usuario inactivo

    ### Ejemplo de uso
    ```python
    # Request
    POST /api/v1/login/access-token/
    {
        "email": "user@example.com",
        "password": "secretpassword"
    }

    # Response
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
    """
    user = await user_repo.authenticate(
        email=login_data.email, password=login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token/", response_model=UserPublic)
async def test_token(current_user: AsyncCurrentUser) -> Any:
    """
    ## Verificar validez del token de acceso

    Endpoint para probar si el token JWT actual es válido y obtener
    información del usuario autenticado.

    ### Autenticación
    Requiere header de autorización: `Authorization: Bearer <token>`

    ### Retorna
    Información pública del usuario autenticado

    ### Errores
    - **401**: Token inválido, expirado o no proporcionado
    - **403**: Usuario inactivo

    ### Ejemplo de uso
    ```python
    # Request
    POST /api/v1/login/test-token/
    Headers: {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }

    # Response
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "full_name": "John Doe",
        "is_active": true,
        "is_superuser": false,
        "role": "viewer"
    }
    ```
    """
    return current_user


@router.post("/password-recovery/{email}/")
async def recover_password(email: str, user_repo: AsyncUserRepoDep) -> Message:
    """
    ## Solicitar recuperación de contraseña

    Envía un email con un token de recuperación de contraseña al usuario.

    ### Parámetros
    - **email**: Email del usuario que solicita recuperar su contraseña

    ### Retorna
    Mensaje de confirmación indicando que se envió el email

    ### Errores
    - **404**: No existe un usuario con ese email

    ### Notas
    - El token de recuperación tiene una validez limitada (configurada en settings)
    - El email contiene un enlace para restablecer la contraseña
    - Por seguridad, siempre devuelve 200 incluso si el email no existe (en producción)

    ### Ejemplo de uso
    ```python
    # Request
    POST /api/v1/password-recovery/user@example.com/

    # Response
    {
        "message": "Password recovery email sent"
    }
    ```
    """
    user = await user_repo.get_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )

    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(user_repo: AsyncUserRepoDep, body: NewPassword) -> Message:
    """
    ## Restablecer contraseña con token

    Permite al usuario establecer una nueva contraseña usando el token
    recibido por email en el proceso de recuperación.

    ### Parámetros
    - **token**: Token de recuperación recibido por email
    - **new_password**: Nueva contraseña que se desea establecer

    ### Retorna
    Mensaje de confirmación de actualización exitosa

    ### Errores
    - **400**: Token inválido o expirado
    - **404**: Usuario no encontrado
    - **400**: Usuario inactivo

    ### Flujo completo
    1. Usuario solicita recuperación en `/password-recovery/{email}/`
    2. Usuario recibe email con token
    3. Usuario envía token + nueva contraseña a este endpoint
    4. Contraseña se actualiza y puede hacer login

    ### Ejemplo de uso
    ```python
    # Request
    POST /api/v1/reset-password/
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "new_password": "newSecurePassword123!"
    }

    # Response
    {
        "message": "Password updated successfully"
    }
    ```
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    user = await user_repo.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    user_repo.session.add(user)
    await user_repo.session.commit()

    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}/",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, user_repo: AsyncUserRepoDep) -> Any:
    """
    ## Obtener contenido HTML del email de recuperación (Solo Superusuarios)

    Endpoint de utilidad para previsualizar el contenido del email de
    recuperación de contraseña. Solo accesible por superusuarios.

    ### Autenticación
    Requiere ser superusuario activo

    ### Parámetros
    - **email**: Email del usuario para generar el email de prueba

    ### Retorna
    HTML del email que se enviaría al usuario

    ### Errores
    - **401**: No autenticado
    - **403**: No es superusuario
    - **404**: Usuario no encontrado

    ### Uso
    Este endpoint es principalmente para:
    - Probar el diseño del email de recuperación
    - Verificar que los templates funcionan correctamente
    - Debugging en desarrollo

    ### Ejemplo de uso
    ```python
    # Request
    POST /api/v1/password-recovery-html-content/user@example.com/
    Headers: {
        "Authorization": "Bearer <superuser_token>"
    }

    # Response
    HTML completo del email con el token de recuperación
    ```
    """
    user = await user_repo.get_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )

    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
