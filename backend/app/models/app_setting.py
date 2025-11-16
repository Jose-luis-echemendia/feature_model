
from typing import Any, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

class AppSetting(SQLModel, table=True):
    """
    Modelo para almacenar configuraciones dinámicas de la aplicación.
    La clave (key) es única y el valor (value) se almacena en un campo JSONB
    para máxima flexibilidad.
    """
    __tablename__ = "app_settings"

    key: str = Field(primary_key=True, max_length=100)
    value: Any = Field(sa_column=Column(JSONB))
    description: Optional[str] = Field(default=None, max_length=255)