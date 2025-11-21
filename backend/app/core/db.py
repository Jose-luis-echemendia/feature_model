import logging

from sqlmodel import Session, create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models import AppSetting, User, UserCreate

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
a_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=False)

# --- imports Data ---
from app.core.data import settings_data
from app.core.data.users import users_data

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    from app.models.user import User, UserCreate
    
    logger.info("Starting database initialization...")

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )

        from app import crud

        user = crud.create_user(session=session, user_create=user_in)

    _create_settings(session)
    _create_example_users(session)
    
    logger.info("Database initialization and seeding completed successfully.")
    
    
def _create_settings(session: Session):
    if session.exec(select(AppSetting)).first():
        logger.info("Settings already exist, skipping creation.")
        return
    
    logger.info("Creating app settings...")
    for key, value, description in settings_data:
        setting = AppSetting(key=key, value=str(value), description=description)
        session.add(setting)
        logger.debug(f"Adding setting: {key}={value}")
    
    session.commit()
    logger.info("App settings created.") 
    
    
    
def _create_example_users(session: Session) -> None:
    if session.exec(select(User).where(User.is_superuser == False)).first():
        logger.info("Non-superuser users already exist, skipping creation.")
        return

    logger.info("Creating example users...")
    from app import crud
    for email, role in users_data:
        user_in = UserCreate(email=email, password="password", role=role)
        crud.user.create_user(session=session, user_create=user_in)
        logger.debug(f"Added user: {email} with role {role.name}")
    session.commit()
    logger.info(f"Created {len(users_data)} example users.")

