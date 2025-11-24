import logging

from sqlmodel import Session, create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models import AppSetting, User, UserCreate

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
a_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=False)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """
    Inicializar la base de datos con datos esenciales

    Esta función se ejecuta al inicio de la aplicación y crea:
    - El superusuario inicial (si no existe)
    - Configuraciones de la aplicación
    - Usuarios de ejemplo (solo en desarrollo)

    Nota: Las tablas deben ser creadas con Alembic migrations
    """

    from app.models.user import User, UserCreate
    from app import crud

    logger.info("Starting database initialization...")

    # Crear superusuario inicial si no existe
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
        logger.info(f"Created first superuser: {settings.FIRST_SUPERUSER}")

    # Importar y ejecutar seeding centralizado
    from app.seed.seeders import seed_settings, seed_production_users

    # Crear settings de la aplicación
    seed_settings(session)

    # Crear usuarios de producción
    seed_production_users(session)

    logger.info("Database initialization completed successfully.")
