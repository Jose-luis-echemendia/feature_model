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

async def check_database() -> bool:
    """
    Health check de la base de datos.
    Verifica conectividad con timeout y retorna bool sin lanzar excepción.
    """
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    from asyncio import timeout
    
    try:
        async with timeout(5.0):  # Timeout de 5 segundos
            async with a_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        logger.debug("db.health_check.ok")
        return True
    except TimeoutError as exc:
        logger.error(
            "db.health_check.timeout",
            timeout_sec=5.0,
            error_type="TimeoutError",
        )
        return False
    except SQLAlchemyError as exc:
        logger.error(
            "db.health_check.failed",
            error=str(exc),
            error_type=type(exc).__name__,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
        )
        return False
    except Exception as exc:
        logger.error(
            "db.health_check.unexpected",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        return False