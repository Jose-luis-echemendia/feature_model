"""Esquemas Pydantic para endpoints de utilidad."""


from pydantic import BaseModel
from app.enums import Environment

class WelcomeResponse(BaseModel):
    """Respuesta del endpoint raíz."""

    message: str
    project: str
    version: str | None = None
    environment: Environment = Environment.DEVELOPMENT
