"""
Módulo principal de seeding

Este módulo orquesta el proceso completo de seeding con diferentes modos:
- Producción: Solo datos esenciales (settings, usuarios de producción)
- Desarrollo: Datos completos incluyendo ejemplos y usuarios de prueba
"""

import logging
import os

from sqlmodel import Session

from app.core.db import engine
from .seeders import (
    seed_settings,
    seed_production_users,
    seed_development_users,
    seed_domains,
    seed_tags,
    seed_resources,
    seed_feature_models,
    get_admin_user,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_production(session: Session) -> None:
    """
    Seeding para entorno de producción

    Solo crea:
    - Configuraciones de aplicación
    - Usuarios de producción (sin contraseñas de prueba)
    """

    logger.info("=" * 70)
    logger.info("🏭 SEEDING DE PRODUCCIÓN")
    logger.info("=" * 70)

    # 1. Settings
    seed_settings(session)

    # 2. Usuarios de producción
    seed_production_users(session)

    logger.info("=" * 70)
    logger.info("✅ SEEDING DE PRODUCCIÓN COMPLETADO")
    logger.info("=" * 70)


def seed_development(session: Session) -> None:
    """
    Seeding para entorno de desarrollo/testing

    Crea todos los datos de ejemplo incluyendo:
    - Usuarios de desarrollo con contraseñas conocidas
    - Dominios de ejemplo
    - Tags
    - Recursos educativos
    - Feature models de ejemplo
    """

    logger.info("=" * 70)
    logger.info("🧪 SEEDING DE DESARROLLO")
    logger.info("=" * 70)

    # 1. Usuarios de desarrollo
    dev_users = seed_development_users(session)

    # 2. Obtener admin para crear otros datos
    admin = get_admin_user(session)
    if not admin:
        logger.error("❌ No se encontró usuario admin, abortando seeding de desarrollo")
        return

    # 3. Dominios
    domains = seed_domains(session, admin)

    # 4. Tags
    tags = seed_tags(session, admin)

    # 5. Recursos educativos
    resources = seed_resources(session, admin)

    # 6. Feature models
    # Buscar usuario designer
    designer = dev_users.get("designer@example.com", admin)
    feature_models = seed_feature_models(session, designer, domains, resources)

    logger.info("=" * 70)
    logger.info("✅ SEEDING DE DESARROLLO COMPLETADO")
    logger.info("=" * 70)
    logger.info("")
    logger.info("📝 CREDENCIALES DE PRUEBA:")
    logger.info("  Admin:        admin@example.com / admin123")
    logger.info("  Designer:     designer@example.com / designer123")
    logger.info("  Editor:       editor@example.com / editor123")
    logger.info("  Configurator: configurator@example.com / config123")
    logger.info("  Viewer:       viewer@example.com / viewer123")
    logger.info("  Reviewer:     reviewer@example.com / reviewer123")
    logger.info("")


def seed_all(environment: str = "local") -> None:
    """
    Ejecutar seeding completo según el entorno

    Args:
        environment: 'local', 'development', 'staging', 'production'
    """

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"🌱 INICIANDO DATABASE SEEDING - Entorno: {environment.upper()}")
    logger.info("=" * 70)
    logger.info("")

    try:
        with Session(engine) as session:
            # Siempre crear settings
            seed_settings(session)

            if environment in ["local", "development"]:
                # Entorno de desarrollo: todo el seeding
                seed_development(session)
            elif environment in ["staging", "production"]:
                # Entorno de producción: solo lo esencial
                seed_production(session)
            else:
                logger.warning(
                    f"⚠️  Entorno '{environment}' no reconocido, usando modo desarrollo"
                )
                seed_development(session)

            logger.info("=" * 70)
            logger.info("✅ DATABASE SEEDING COMPLETADO EXITOSAMENTE")
            logger.info("=" * 70)
            logger.info("")

    except Exception as e:
        logger.error(f"❌ Error durante el seeding: {e}")
        logger.exception("Detalles del error:")
        raise


def main():
    """Función principal para ejecutar desde línea de comandos"""

    # Obtener entorno de variable de entorno
    environment = os.getenv("ENVIRONMENT", "local")

    seed_all(environment=environment)


if __name__ == "__main__":
    main()
