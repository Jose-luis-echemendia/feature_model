"""
Script para poblar la base de datos con datos de prueba (Database Seeding)

Este script crea datos de ejemplo para facilitar el desarrollo y testing:
- Usuarios de prueba con diferentes roles
- Dominios de ejemplo
- Modelos de características de muestra
- Configuraciones de ejemplo

Uso:
    python -m app.seed_data
"""

import asyncio
import logging
from uuid import uuid4

from sqlmodel import Session, select

from app.core.db import engine
from app.models import (
    User,
    Domain,
    FeatureModel,
    FeatureModelVersion,
    Feature,
    Tag,
    Resource,
)
from app.core.security import get_password_hash
from app.enums import (
    UserRole,
    FeatureType,
    ModelStatus,
    ResourceType,
    ResourceStatus,
    LicenseType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_users(session: Session) -> dict[str, User]:
    """Crear usuarios de prueba con diferentes roles"""

    logger.info("🌱 Sembrando usuarios de prueba...")

    users = {}

    # Verificar si ya existe el admin principal
    admin = session.exec(select(User).where(User.email == "admin@example.com")).first()

    if admin:
        logger.info("  ℹ️  Usuario admin ya existe, omitiendo...")
        users["admin"] = admin
    else:
        # Usuario Admin
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_superuser=True,
            is_active=True,
            role=UserRole.ADMIN,
        )
        session.add(admin)
        session.flush()
        users["admin"] = admin
        logger.info(f"  ✅ Creado usuario: {admin.email} (Admin)")

    # Diseñador de modelos
    designer = session.exec(
        select(User).where(User.email == "designer@example.com")
    ).first()

    if not designer:
        designer = User(
            email="designer@example.com",
            hashed_password=get_password_hash("designer123"),
            is_superuser=False,
            is_active=True,
            role=UserRole.MODEL_DESIGNER,
            created_by_id=admin.id,
        )
        session.add(designer)
        session.flush()
        logger.info(f"  ✅ Creado usuario: {designer.email} (Designer)")
    users["designer"] = designer

    # Editor de modelos
    editor = session.exec(
        select(User).where(User.email == "editor@example.com")
    ).first()

    if not editor:
        editor = User(
            email="editor@example.com",
            hashed_password=get_password_hash("editor123"),
            is_superuser=False,
            is_active=True,
            role=UserRole.MODEL_EDITOR,
            created_by_id=admin.id,
        )
        session.add(editor)
        session.flush()
        logger.info(f"  ✅ Creado usuario: {editor.email} (Editor)")
    users["editor"] = editor

    # Configurador
    configurator = session.exec(
        select(User).where(User.email == "configurator@example.com")
    ).first()

    if not configurator:
        configurator = User(
            email="configurator@example.com",
            hashed_password=get_password_hash("config123"),
            is_superuser=False,
            is_active=True,
            role=UserRole.CONFIGURATOR,
            created_by_id=admin.id,
        )
        session.add(configurator)
        session.flush()
        logger.info(f"  ✅ Creado usuario: {configurator.email} (Configurator)")
    users["configurator"] = configurator

    # Viewer
    viewer = session.exec(
        select(User).where(User.email == "viewer@example.com")
    ).first()

    if not viewer:
        viewer = User(
            email="viewer@example.com",
            hashed_password=get_password_hash("viewer123"),
            is_superuser=False,
            is_active=True,
            role=UserRole.VIEWER,
            created_by_id=admin.id,
        )
        session.add(viewer)
        session.flush()
        logger.info(f"  ✅ Creado usuario: {viewer.email} (Viewer)")
    users["viewer"] = viewer

    session.commit()
    logger.info(f"✅ Usuarios sembrados: {len(users)} usuarios creados")

    return users


def seed_domains(session: Session, users: dict) -> list[Domain]:
    """Crear dominios de ejemplo"""

    logger.info("🌱 Sembrando dominios de ejemplo...")

    domains_data = [
        {
            "name": "E-Commerce",
            "description": "Dominio para sistemas de comercio electrónico",
        },
        {
            "name": "Healthcare",
            "description": "Dominio para aplicaciones de salud y medicina",
        },
        {
            "name": "Education",
            "description": "Dominio para plataformas educativas y e-learning",
        },
        {
            "name": "IoT",
            "description": "Dominio para Internet de las Cosas y dispositivos conectados",
        },
    ]

    domains = []
    admin = users["admin"]

    for domain_data in domains_data:
        # Verificar si ya existe
        existing = session.exec(
            select(Domain).where(Domain.name == domain_data["name"])
        ).first()

        if existing:
            logger.info(f"  ℹ️  Dominio '{domain_data['name']}' ya existe, omitiendo...")
            domains.append(existing)
            continue

        domain = Domain(
            **domain_data,
            created_by_id=admin.id,
            is_active=True,
        )
        session.add(domain)
        domains.append(domain)
        logger.info(f"  ✅ Creado dominio: {domain.name}")

    session.commit()
    logger.info(f"✅ Dominios sembrados: {len(domains)} dominios")

    return domains


def seed_tags(session: Session, users: dict) -> list[Tag]:
    """Crear tags de ejemplo"""

    logger.info("🌱 Sembrando tags de ejemplo...")

    tags_data = [
        {
            "name": "performance",
            "description": "Características relacionadas con rendimiento",
        },
        {"name": "security", "description": "Características de seguridad"},
        {"name": "ui", "description": "Interfaz de usuario"},
        {"name": "api", "description": "Integración con APIs"},
        {"name": "mobile", "description": "Funcionalidad móvil"},
        {"name": "analytics", "description": "Análisis y métricas"},
        {"name": "payment", "description": "Procesamiento de pagos"},
        {"name": "authentication", "description": "Autenticación y autorización"},
    ]

    tags = []
    admin = users["admin"]

    for tag_data in tags_data:
        # Verificar si ya existe
        existing = session.exec(select(Tag).where(Tag.name == tag_data["name"])).first()

        if existing:
            logger.info(f"  ℹ️  Tag '{tag_data['name']}' ya existe, omitiendo...")
            tags.append(existing)
            continue

        tag = Tag(
            **tag_data,
            created_by_id=admin.id,
            is_active=True,
        )
        session.add(tag)
        tags.append(tag)
        logger.info(f"  ✅ Creado tag: {tag.name}")

    session.commit()
    logger.info(f"✅ Tags sembrados: {len(tags)} tags")

    return tags


def seed_resources(session: Session, users: dict) -> list[Resource]:
    """Crear recursos educativos de ejemplo"""

    logger.info("🌱 Sembrando recursos educativos...")

    resources_data = [
        {
            "title": "Introducción a Feature Models",
            "type": ResourceType.VIDEO,
            "description": "Video tutorial sobre conceptos básicos de feature modeling",
            "language": "es",
            "duration_minutes": 15,
            "status": ResourceStatus.PUBLISHED,
            "license": LicenseType.CREATIVE_COMMONS_BY,
            "content_url_or_data": {"url": "https://example.com/videos/intro-fm"},
        },
        {
            "title": "Guía de Configuración",
            "type": ResourceType.PDF,
            "description": "Documento PDF con guía completa de configuración",
            "language": "es",
            "status": ResourceStatus.PUBLISHED,
            "license": LicenseType.CREATIVE_COMMONS_BY_SA,
            "content_url_or_data": {"url": "https://example.com/docs/config-guide.pdf"},
        },
        {
            "title": "Quiz de Feature Modeling",
            "type": ResourceType.QUIZ,
            "description": "Evaluación de conocimientos básicos",
            "language": "es",
            "duration_minutes": 10,
            "status": ResourceStatus.PUBLISHED,
            "license": LicenseType.INTERNAL_USE,
            "content_url_or_data": {
                "questions": [
                    {
                        "question": "¿Qué es un feature model?",
                        "options": ["A", "B", "C", "D"],
                        "correct": 0,
                    }
                ]
            },
        },
    ]

    resources = []
    admin = users["admin"]

    for resource_data in resources_data:
        # Verificar si ya existe
        existing = session.exec(
            select(Resource).where(Resource.title == resource_data["title"])
        ).first()

        if existing:
            logger.info(
                f"  ℹ️  Recurso '{resource_data['title']}' ya existe, omitiendo..."
            )
            resources.append(existing)
            continue

        resource = Resource(
            **resource_data,
            version=1,
            owner_id=admin.id,
            created_by_id=admin.id,
            is_active=True,
        )
        session.add(resource)
        resources.append(resource)
        logger.info(f"  ✅ Creado recurso: {resource.title}")

    session.commit()
    logger.info(f"✅ Recursos sembrados: {len(resources)} recursos")

    return resources


def seed_feature_models(
    session: Session, users: dict, domains: list[Domain], resources: list[Resource]
) -> None:
    """Crear modelos de características de ejemplo con sus versiones y features"""

    logger.info("🌱 Sembrando modelos de características...")

    designer = users["designer"]
    ecommerce_domain = next((d for d in domains if d.name == "E-Commerce"), domains[0])

    # Verificar si ya existe
    existing_model = session.exec(
        select(FeatureModel).where(FeatureModel.name == "E-Commerce Platform")
    ).first()

    if existing_model:
        logger.info("  ℹ️  Modelo 'E-Commerce Platform' ya existe, omitiendo...")
        return

    # Crear Feature Model
    feature_model = FeatureModel(
        name="E-Commerce Platform",
        description="Modelo de características para una plataforma de comercio electrónico",
        domain_id=ecommerce_domain.id,
        owner_id=designer.id,
        created_by_id=designer.id,
        is_active=True,
    )
    session.add(feature_model)
    session.flush()
    logger.info(f"  ✅ Creado modelo: {feature_model.name}")

    # Crear Version del modelo
    model_version = FeatureModelVersion(
        version_number=1,
        feature_model_id=feature_model.id,
        status=ModelStatus.PUBLISHED,
        created_by_id=designer.id,
        is_active=True,
    )
    session.add(model_version)
    session.flush()
    logger.info(f"    ✅ Creada versión: v{model_version.version_number}")

    # Crear Features jerárquicas
    # Feature raíz
    root_feature = Feature(
        name="E-Commerce System",
        type=FeatureType.MANDATORY,
        feature_model_version_id=model_version.id,
        created_by_id=designer.id,
        is_active=True,
        properties={"description": "Sistema completo de comercio electrónico"},
    )
    session.add(root_feature)
    session.flush()
    logger.info(f"      ✅ Feature: {root_feature.name} (root)")

    # Sub-features
    features_data = [
        {
            "name": "Product Catalog",
            "type": FeatureType.MANDATORY,
            "parent": root_feature,
        },
        {
            "name": "Shopping Cart",
            "type": FeatureType.MANDATORY,
            "parent": root_feature,
        },
        {
            "name": "Payment Processing",
            "type": FeatureType.MANDATORY,
            "parent": root_feature,
        },
        {
            "name": "User Management",
            "type": FeatureType.MANDATORY,
            "parent": root_feature,
        },
        {"name": "Wishlist", "type": FeatureType.OPTIONAL, "parent": root_feature},
        {
            "name": "Product Reviews",
            "type": FeatureType.OPTIONAL,
            "parent": root_feature,
        },
        {
            "name": "Recommendations",
            "type": FeatureType.OPTIONAL,
            "parent": root_feature,
        },
    ]

    for feature_data in features_data:
        parent = feature_data.pop("parent")
        feature = Feature(
            **feature_data,
            feature_model_version_id=model_version.id,
            parent_id=parent.id if parent else None,
            resource_id=resources[0].id if resources else None,
            created_by_id=designer.id,
            is_active=True,
            properties={"level": 1},
        )
        session.add(feature)
        logger.info(f"      ✅ Feature: {feature.name} ({feature.type.value})")

    session.commit()
    logger.info("✅ Modelos de características sembrados")


def main():
    """Función principal para ejecutar el seeding"""

    logger.info("=" * 60)
    logger.info("🌱 INICIANDO DATABASE SEEDING")
    logger.info("=" * 60)

    try:
        with Session(engine) as session:
            # 1. Crear usuarios
            users = seed_users(session)

            # 2. Crear dominios
            domains = seed_domains(session, users)

            # 3. Crear tags
            tags = seed_tags(session, users)

            # 4. Crear recursos
            resources = seed_resources(session, users)

            # 5. Crear feature models con features
            seed_feature_models(session, users, domains, resources)

            logger.info("=" * 60)
            logger.info("✅ DATABASE SEEDING COMPLETADO EXITOSAMENTE")
            logger.info("=" * 60)
            logger.info("")
            logger.info("📝 CREDENCIALES DE PRUEBA:")
            logger.info("  Admin:        admin@example.com / admin123")
            logger.info("  Designer:     designer@example.com / designer123")
            logger.info("  Editor:       editor@example.com / editor123")
            logger.info("  Configurator: configurator@example.com / config123")
            logger.info("  Viewer:       viewer@example.com / viewer123")
            logger.info("")

    except Exception as e:
        logger.error(f"❌ Error durante el seeding: {e}")
        raise


if __name__ == "__main__":
    main()
