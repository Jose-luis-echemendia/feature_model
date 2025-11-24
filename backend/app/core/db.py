import logging

from sqlmodel import Session, create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
a_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=False)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """
    Inicializar conexión a la base de datos

    IMPORTANTE: Esta función SOLO verifica la conexión a la base de datos.
    NO crea datos - eso lo hace el módulo app.seed.main

    El seeding se ejecuta desde scripts/prestart.sh llamando a:
        python -m app.seed.main
    """

    logger.info("Verificando conexión a la base de datos...")

    # Simplemente verificar que la sesión funciona
    try:
        # Hacer una query simple para verificar conexión
        session.exec(select(1)).first()
        logger.info("✅ Conexión a la base de datos verificada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al conectar con la base de datos: {e}")
        raise
