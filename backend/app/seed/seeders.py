"""
Funciones de seeding para poblar la base de datos

Este módulo contiene todas las funciones necesarias para crear
datos de prueba en la base de datos de manera idempotente.
"""

import logging, uuid
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
from app.enums import UserRole, FeatureGroupType

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
# HELPER FUNCTIONS
# ==============================================================================
def _normalize_group_type(group_type: str) -> FeatureGroupType:
    """
    Normaliza los tipos de grupo del seeder a los valores del enum.

    Mapeo:
    - "XOR" -> FeatureGroupType.ALTERNATIVE (solo una opción)
    - "OR" -> FeatureGroupType.OR (una o más opciones)
    - "alternative" -> FeatureGroupType.ALTERNATIVE
    - "or" -> FeatureGroupType.OR
    """
    type_mapping = {
        "XOR": FeatureGroupType.ALTERNATIVE,
        "OR": FeatureGroupType.OR,
        "alternative": FeatureGroupType.ALTERNATIVE,
        "or": FeatureGroupType.OR,
    }

    normalized = type_mapping.get(group_type)
    if normalized is None:
        logger.warning(
            f"⚠️ Tipo de grupo desconocido: '{group_type}'. Usando ALTERNATIVE por defecto."
        )
        return FeatureGroupType.ALTERNATIVE

    return normalized


# ==============================================================================
# FIRST SUPERUSER
# ==============================================================================
def create_first_superuser(session: Session) -> Optional[User]:
    """
    Crear el primer superusuario desde variables de entorno

    Este usuario se crea SIEMPRE en todos los entornos (producción y desarrollo)
    y es el administrador principal del sistema.
    """
    from app.core.config import settings

    logger.info("🌱 Creando FIRST_SUPERUSER...")

    # Verificar si ya existe
    existing = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()

    if existing:
        logger.info(
            f"  ℹ️  FIRST_SUPERUSER '{settings.FIRST_SUPERUSER}' ya existe, omitiendo..."
        )
        return existing

    # Crear el primer superusuario
    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        role=UserRole.DEVELOPER,
    )

    user = crud.create_user(session=session, user_create=user_in)
    session.commit()

    logger.info(f"  ✅ FIRST_SUPERUSER creado: {settings.FIRST_SUPERUSER}")
    return user


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
    """Crear dominios académicos de ejemplo"""

    logger.info("🌱 Sembrando dominios académicos...")

    domains = []

    for domain_data in domains_data:
        # Verificar si ya existe
        existing = session.exec(
            select(Domain).where(Domain.name == domain_data["name"])
        ).first()

        if existing:
            logger.info(
                f"  ℹ️  Dominio académico '{domain_data['name']}' ya existe, omitiendo..."
            )
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
    logger.info(f"✅ Dominios académicos sembrados: {len(domains)} dominios")

    return domains


# ==============================================================================
# TAGS
# ==============================================================================
def seed_tags(session: Session, owner: User) -> list[Tag]:
    """Crear tags pedagógicos de ejemplo"""

    logger.info("🌱 Sembrando etiquetas pedagógicas...")

    tags = []

    for tag_data in tags_data:
        # Verificar si ya existe
        existing = session.exec(select(Tag).where(Tag.name == tag_data["name"])).first()

        if existing:
            logger.info(f"  ℹ️  Etiqueta '{tag_data['name']}' ya existe, omitiendo...")
            tags.append(existing)
            continue

        tag = Tag(
            **tag_data,
            created_by_id=owner.id,
            is_active=True,
        )
        session.add(tag)
        tags.append(tag)
        logger.info(f"  ✅ Creada etiqueta: {tag.name}")

    session.commit()
    logger.info(f"✅ Etiquetas pedagógicas sembradas: {len(tags)} tags")

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
    resources: Optional[
        list[Resource]
    ] = None,  # Se recibe la lista de recursos creados
) -> list[FeatureModel]:
    """Crear planes de estudio y modelos curriculares de ejemplo"""

    # Importaciones necesarias dentro de la función para evitar ciclos
    from app.models import Tag

    logger.info("🌱 Sembrando planes de estudio y modelos curriculares...")

    # ----------------------------------------------------------------------
    # 1. PREPARACIÓN DE MAPAS DE BÚSQUEDA (Lookup Maps)
    # ----------------------------------------------------------------------
    # Para no hacer una query por cada feature, cargamos diccionarios en memoria.

    # Mapa de Recursos: Título -> UUID
    resource_map = {r.title: r.id for r in (resources or [])}

    # Mapa de Tags: Nombre -> UUID
    all_tags = session.exec(select(Tag)).all()
    tag_map = {t.name: t.id for t in all_tags}

    models = []

    for model_data in feature_models_data:
        # Verificar si ya existe el modelo
        existing = session.exec(
            select(FeatureModel).where(FeatureModel.name == model_data["name"])
        ).first()

        if existing:
            logger.info(f"  ℹ️  Plan '{model_data['name']}' ya existe, omitiendo...")
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
        logger.info(f"  ✅ Creado plan: {feature_model.name}")

        # Crear Versión
        version_data = model_data["version"]
        model_version = FeatureModelVersion(
            version_number=version_data["version_number"],
            feature_model_id=feature_model.id,
            status=version_data["status"],
            created_by_id=owner.id,
            is_active=True,
            snapshot={},
        )
        session.add(model_version)
        session.flush()

        # Preparar mapas para recursión
        feature_map = {}
        solver_map = {"uuid_to_int": {}, "int_to_uuid": {}}
        counter = [1]

        # Crear Features Recursivamente
        for feature_data in version_data["features"]:
            _create_feature_recursive(
                session=session,
                feature_data=feature_data,
                version_id=model_version.id,
                owner_id=owner.id,
                parent_id=None,
                group_id=None,
                # Pasamos los mapas de búsqueda en lugar de un ID fijo
                resource_map=resource_map,
                tag_map=tag_map,
                feature_map=feature_map,
                solver_map=solver_map,
                counter=counter,
            )

        # Relaciones y Constraints (Igual que antes)
        if "feature_relations" in version_data:
            _create_feature_relations(
                session,
                version_data["feature_relations"],
                feature_map,
                owner.id,
                model_version.id,
            )

        if "constraints" in version_data:
            _create_constraints(
                session, version_data["constraints"], model_version.id, owner.id
            )

        model_version.snapshot = solver_map
        session.add(model_version)

    session.commit()
    logger.info(f"✅ Planes sembrados: {len(models)}")
    return models


def _create_feature_recursive(
    session: Session,
    feature_data: dict,
    version_id: uuid.UUID,
    owner_id: uuid.UUID,
    resource_map: dict,  # Diccionario {Titulo: ID}
    tag_map: dict,  # Diccionario {Nombre: ID}
    parent_id: Optional[uuid.UUID] = None,
    group_id: Optional[uuid.UUID] = None,
    feature_map: Optional[dict] = None,
    solver_map: Optional[dict] = None,
    counter: list[int] = None,
) -> Feature:

    from app.models import FeatureTagLink, FeatureGroup

    # 1. Resolver el Resource ID específico para esta feature
    # Buscamos por el título que viene en el JSON. Si no hay, es None.
    specific_resource_id = None
    resource_title = feature_data.get("resource_title")  # Clave nueva en JSON

    if resource_title:
        specific_resource_id = resource_map.get(resource_title)
        if not specific_resource_id:
            logger.warning(
                f"    ⚠️ Recurso '{resource_title}' no encontrado para feature '{feature_data['name']}'"
            )

    # 2. Extraer datos hijos
    direct_children = feature_data.get("children", [])
    child_groups_data = feature_data.get("groups", [])

    # 3. Crear Feature
    feature = Feature(
        name=feature_data["name"],
        type=feature_data["type"],
        properties=feature_data.get("properties", {}),
        feature_model_version_id=version_id,
        parent_id=parent_id,
        group_id=group_id,
        resource_id=specific_resource_id,  # Asignación dinámica
        created_by_id=owner_id,
        is_active=True,
    )
    session.add(feature)
    session.flush()  # Necesario para obtener feature.id

    # 4. Vincular TAGS (Many-to-Many)
    # El JSON trae: "tags": ["teórico", "difícil"]
    tag_names = feature_data.get("tags", [])

    for t_name in tag_names:
        tag_id = tag_map.get(t_name)
        if tag_id:
            # Crear enlace en tabla intermedia
            link = FeatureTagLink(feature_id=feature.id, tag_id=tag_id)
            session.add(link)
        else:
            logger.warning(f"    ⚠️ Tag '{t_name}' no encontrado en el sistema.")

    # 5. Registrar en mapas (Lógica existente)
    if feature_map is not None:
        feature_map[feature.name] = feature

    if solver_map is not None and counter is not None:
        current_int = counter[0]
        f_uuid_str = str(feature.id)
        solver_map["uuid_to_int"][f_uuid_str] = current_int
        solver_map["int_to_uuid"][str(current_int)] = f_uuid_str
        counter[0] += 1

    # 6. Recursividad (Hijos)
    for child_data in direct_children:
        _create_feature_recursive(
            session,
            child_data,
            version_id,
            owner_id,
            resource_map,
            tag_map,
            parent_id=feature.id,
            group_id=None,
            feature_map=feature_map,
            solver_map=solver_map,
            counter=counter,
        )

    # 7. Recursividad (Grupos)
    for group_data in child_groups_data:
        # Normalizar el tipo de grupo (XOR -> ALTERNATIVE, OR -> OR)
        normalized_type = _normalize_group_type(group_data["type"])

        feature_group = FeatureGroup(
            group_type=normalized_type,
            min_cardinality=group_data.get("min", 1),
            max_cardinality=group_data.get("max", 1),
            parent_feature_id=feature.id,
            feature_model_version_id=version_id,
            created_by_id=owner_id,
            is_active=True,
        )
        session.add(feature_group)
        session.flush()

        for group_child_data in group_data["features"]:
            _create_feature_recursive(
                session,
                group_child_data,
                version_id,
                owner_id,
                resource_map,
                tag_map,
                parent_id=None,
                group_id=feature_group.id,
                feature_map=feature_map,
                solver_map=solver_map,
                counter=counter,
            )

    return feature


def _create_feature_relations(
    session: Session,
    relations_data: list[dict],
    feature_map: dict,
    owner_id: uuid.UUID,
    version_id: uuid.UUID,  # Este argumento es obligatorio
) -> None:
    """Crear relaciones simples (Requires/Excludes)"""
    from app.enums import FeatureRelationType
    from app.models import FeatureRelation  # Import local por si acaso

    logger.info("    🔗 Creando relaciones entre features...")

    for relation_data in relations_data:
        source = feature_map.get(relation_data["source"])
        target = feature_map.get(relation_data["target"])

        if source and target:
            relation = FeatureRelation(
                source_feature_id=source.id,
                target_feature_id=target.id,
                feature_model_version_id=version_id,  # Asignación correcta
                type=(  # El campo se llama 'type', NO 'relation_type'
                    FeatureRelationType.REQUIRED
                    if relation_data["type"] == "requires"
                    else FeatureRelationType.EXCLUDES
                ),
                created_by_id=owner_id,
                is_active=True,
            )
            session.add(relation)
            logger.info(f"      ✅ Relación: {source.name} -> {target.name}")

    session.flush()


def _create_constraints(
    session: Session,
    constraints_data: list[dict],
    version_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> None:
    """Crear restricciones avanzadas"""
    from app.models import Constraint

    logger.info("    📐 Creando restricciones avanzadas...")

    for c_data in constraints_data:
        # Nota: Aquí no estamos calculando el 'expr_cnf' automáticamente
        # porque requeriría un parser lógico complejo.
        # Se asume que el seeder viene con texto o CNF pre-calculado si fuera necesario.

        constraint = Constraint(
            expr_text=c_data["expr"],  # Ej: "A or (B and not C)"
            description=c_data.get("description"),
            feature_model_version_id=version_id,
            created_by_id=owner_id,
            is_active=True,
            # expr_cnf=... (Opcional: Si tu data_models ya tiene los enteros calculados)
        )
        session.add(constraint)
        logger.info(
            f"      ✅ Constraint: {c_data.get('description', 'Sin descripción')}"
        )

    session.flush()


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
