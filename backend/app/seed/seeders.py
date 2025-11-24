"""
Funciones de seeding para poblar la base de datos

Este módulo contiene todas las funciones necesarias para crear
datos de prueba en la base de datos de manera idempotente.
"""

import logging
from typing import Optional

from sqlmodel import Session, select

from app.models import (
    User,
    AppSetting,
    Domain,
    Tag,
    Resource,
    FeatureModel,
    FeatureModelVersion,
    Feature,
)
from app.core.security import get_password_hash
from app import crud
from app.models.user import UserCreate
from app.enums import UserRole

# Importar datos
from .data_settings import settings_data
from .data_users import production_users, development_users
from .data_models import (
    domains_data,
    tags_data,
    resources_data,
    feature_models_data,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# SETTINGS
# ==============================================================================
def seed_settings(session: Session) -> None:
    """Crear configuraciones de la aplicación"""

    logger.info("🌱 Sembrando configuraciones de aplicación...")

    if session.exec(select(AppSetting)).first():
        logger.info("  ℹ️  Configuraciones ya existen, omitiendo...")
        return

    for key, value, description in settings_data:
        setting = AppSetting(key=key, value=str(value), description=description)
        session.add(setting)
        logger.debug(f"  ➕ Agregando setting: {key}={value}")

    session.commit()
    logger.info(f"✅ Configuraciones sembradas: {len(settings_data)} settings")


# ==============================================================================
# USERS - PRODUCTION
# ==============================================================================
def seed_production_users(session: Session) -> dict[str, User]:
    """Crear usuarios de producción (sin contraseña predeterminada)"""

    logger.info("🌱 Sembrando usuarios de producción...")

    users = {}

    for email, role in production_users:
        # Verificar si ya existe
        existing = session.exec(select(User).where(User.email == email)).first()

        if existing:
            logger.info(f"  ℹ️  Usuario '{email}' ya existe, omitiendo...")
            users[email] = existing
            continue

        # Crear usuario (la contraseña se establecerá por email)
        user_in = UserCreate(
            email=email,
            password="ChangeMe123!",  # Contraseña temporal
            role=role,
        )

        user = crud.create_user(session=session, user_create=user_in)
        users[email] = user
        logger.info(f"  ✅ Creado usuario: {email} ({role.value})")

    session.commit()
    logger.info(f"✅ Usuarios de producción sembrados: {len(users)} usuarios")

    return users


# ==============================================================================
# USERS - DEVELOPMENT
# ==============================================================================
def seed_development_users(session: Session) -> dict[str, User]:
    """Crear usuarios de desarrollo/testing con contraseñas conocidas"""

    logger.info("🌱 Sembrando usuarios de desarrollo...")

    users = {}

    # Obtener admin para asignar como created_by
    admin = session.exec(select(User).where(User.email == "admin@example.com")).first()

    for email, password, role, is_superuser in development_users:
        # Verificar si ya existe
        existing = session.exec(select(User).where(User.email == email)).first()

        if existing:
            logger.info(f"  ℹ️  Usuario '{email}' ya existe, omitiendo...")
            users[email] = existing
            continue

        # Crear usuario con contraseña conocida
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            is_superuser=is_superuser,
            is_active=True,
            role=role,
            created_by_id=admin.id if admin and not is_superuser else None,
        )
        session.add(user)
        session.flush()
        users[email] = user
        logger.info(f"  ✅ Creado usuario: {email} ({role.value}) - pwd: {password}")

    session.commit()
    logger.info(f"✅ Usuarios de desarrollo sembrados: {len(users)} usuarios")

    return users


# ==============================================================================
# DOMAINS
# ==============================================================================
def seed_domains(session: Session, owner: User) -> list[Domain]:
    """Crear dominios de ejemplo"""

    logger.info("🌱 Sembrando dominios...")

    domains = []

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
            created_by_id=owner.id,
            is_active=True,
        )
        session.add(domain)
        domains.append(domain)
        logger.info(f"  ✅ Creado dominio: {domain.name}")

    session.commit()
    logger.info(f"✅ Dominios sembrados: {len(domains)} dominios")

    return domains


# ==============================================================================
# TAGS
# ==============================================================================
def seed_tags(session: Session, owner: User) -> list[Tag]:
    """Crear tags de ejemplo"""

    logger.info("🌱 Sembrando tags...")

    tags = []

    for tag_data in tags_data:
        # Verificar si ya existe
        existing = session.exec(select(Tag).where(Tag.name == tag_data["name"])).first()

        if existing:
            logger.info(f"  ℹ️  Tag '{tag_data['name']}' ya existe, omitiendo...")
            tags.append(existing)
            continue

        tag = Tag(
            **tag_data,
            created_by_id=owner.id,
            is_active=True,
        )
        session.add(tag)
        tags.append(tag)
        logger.info(f"  ✅ Creado tag: {tag.name}")

    session.commit()
    logger.info(f"✅ Tags sembrados: {len(tags)} tags")

    return tags


# ==============================================================================
# RESOURCES
# ==============================================================================
def seed_resources(session: Session, owner: User) -> list[Resource]:
    """Crear recursos educativos de ejemplo"""

    logger.info("🌱 Sembrando recursos educativos...")

    resources = []

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
            owner_id=owner.id,
            created_by_id=owner.id,
            is_active=True,
        )
        session.add(resource)
        resources.append(resource)
        logger.info(f"  ✅ Creado recurso: {resource.title}")

    session.commit()
    logger.info(f"✅ Recursos sembrados: {len(resources)} recursos")

    return resources


# ==============================================================================
# FEATURE MODELS
# ==============================================================================
def seed_feature_models(
    session: Session,
    owner: User,
    domains: list[Domain],
    resources: Optional[list[Resource]] = None,
) -> list[FeatureModel]:
    """Crear modelos de características de ejemplo"""

    logger.info("🌱 Sembrando modelos de características...")

    models = []

    for model_data in feature_models_data:
        # Verificar si ya existe
        existing = session.exec(
            select(FeatureModel).where(FeatureModel.name == model_data["name"])
        ).first()

        if existing:
            logger.info(f"  ℹ️  Modelo '{model_data['name']}' ya existe, omitiendo...")
            models.append(existing)
            continue

        # Buscar dominio
        domain = next(
            (d for d in domains if d.name == model_data["domain_name"]), domains[0]
        )

        # Crear Feature Model
        feature_model = FeatureModel(
            name=model_data["name"],
            description=model_data["description"],
            domain_id=domain.id,
            owner_id=owner.id,
            created_by_id=owner.id,
            is_active=True,
        )
        session.add(feature_model)
        session.flush()
        models.append(feature_model)
        logger.info(f"  ✅ Creado modelo: {feature_model.name}")

        # Crear versión del modelo
        version_data = model_data["version"]
        model_version = FeatureModelVersion(
            version_number=version_data["version_number"],
            feature_model_id=feature_model.id,
            status=version_data["status"],
            created_by_id=owner.id,
            is_active=True,
        )
        session.add(model_version)
        session.flush()
        logger.info(f"    ✅ Creada versión: v{model_version.version_number}")

        # Crear features recursivamente
        for feature_data in version_data["features"]:
            _create_feature_recursive(
                session,
                feature_data,
                model_version.id,
                owner.id,
                parent_id=None,
                resource_id=resources[0].id if resources else None,
            )

    session.commit()
    logger.info(f"✅ Modelos sembrados: {len(models)} modelos")

    return models


def _create_feature_recursive(
    session: Session,
    feature_data: dict,
    version_id: int,
    owner_id: int,
    parent_id: Optional[int] = None,
    resource_id: Optional[int] = None,
) -> Feature:
    """Crear feature y sus hijos recursivamente"""

    children = feature_data.pop("children", [])

    feature = Feature(
        name=feature_data["name"],
        type=feature_data["type"],
        properties=feature_data.get("properties", {}),
        feature_model_version_id=version_id,
        parent_id=parent_id,
        resource_id=resource_id,
        created_by_id=owner_id,
        is_active=True,
    )
    session.add(feature)
    session.flush()

    indent = "      " if parent_id else "    "
    logger.info(f"{indent}✅ Feature: {feature.name} ({feature.type.value})")

    # Crear hijos
    for child_data in children:
        _create_feature_recursive(
            session, child_data, version_id, owner_id, feature.id, resource_id
        )

    return feature


# ==============================================================================
# HELPER FUNCTION
# ==============================================================================
def get_admin_user(session: Session) -> Optional[User]:
    """Obtener el primer usuario admin disponible"""

    # Intentar obtener admin de desarrollo
    admin = session.exec(select(User).where(User.email == "admin@example.com")).first()

    if admin:
        return admin

    # Obtener cualquier superuser
    admin = session.exec(select(User).where(User.is_superuser == True)).first()

    if admin:
        return admin

    # Obtener cualquier admin
    admin = session.exec(select(User).where(User.role == UserRole.ADMIN)).first()

    return admin
