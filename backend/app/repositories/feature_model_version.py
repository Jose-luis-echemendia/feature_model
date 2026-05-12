import uuid
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Feature,
    FeatureModel,
    FeatureModelVersion,
    FeatureRelation,
    User,
)
from app.enums import ModelStatus
from app.repositories.base import BaseFeatureModelVersionRepository


class FeatureModelVersionRepository(BaseFeatureModelVersionRepository):
    """Implementación asíncrona del repositorio de versiones de feature models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, version_id: uuid.UUID) -> FeatureModelVersion | None:
        """Obtener una versión de modelo por su ID."""
        stmt = select(FeatureModelVersion).where(FeatureModelVersion.id == version_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_version_number(self, feature_model_id: uuid.UUID) -> int:
        """Obtener el número de la última versión para un modelo."""
        statement = select(FeatureModelVersion.version_number).where(
            FeatureModelVersion.feature_model_id == feature_model_id
        )
        result = await self.session.execute(statement)
        versions = result.all()
        return max((v[0] for v in versions), default=0)

    async def get_latest_published_version(
        self, feature_model_id: uuid.UUID
    ) -> FeatureModelVersion | None:
        """
        Obtener la última versión con status PUBLISHED para un feature model.

        Returns:
            FeatureModelVersion o None si no existe ninguna versión publicada.
        """
        stmt = (
            select(FeatureModelVersion)
            .where(
                FeatureModelVersion.feature_model_id == feature_model_id,
                FeatureModelVersion.status == ModelStatus.PUBLISHED,
            )
            .order_by(FeatureModelVersion.version_number.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_new_version_from_existing(
        self,
        source_version: FeatureModelVersion,
        user: User,
        return_id_map: bool = False,
    ) -> (
        FeatureModelVersion
        | tuple[
            FeatureModelVersion, dict[uuid.UUID, uuid.UUID], dict[uuid.UUID, uuid.UUID]
        ]
    ):
        """
        Crea una nueva versión de un modelo de características, clonando todas las
        features y relaciones de una versión de origen. (Copy-On-Write)

        Nota: Utiliza run_sync para ejecutar la lógica sync del repositorio.
        """

        def _create_version_sync(sync_session):
            from app.repositories.feature_model_version import (
                FeatureModelVersionRepository,
            )

            sync_repo = FeatureModelVersionRepository(sync_session)
            return sync_repo.create_new_version_from_existing(
                source_version=source_version,
                user=user,
                return_id_map=return_id_map,
            )

        # Ejecutar la lógica sync dentro del contexto async
        result = await self.session.run_sync(_create_version_sync)
        return result

    async def exists(self, version_id: uuid.UUID) -> bool:
        """Verificar si una versión existe."""
        version = await self.get(version_id)
        return version is not None

    async def get_complete_with_relations(
        self, version_id: uuid.UUID, include_resources: bool = True
    ) -> FeatureModelVersion | None:
        """
        Obtener una versión completa con TODAS sus relaciones cargadas (eager loading).
        Optimizado para construir el árbol completo en una sola query.

        MEJORAS DE PERFORMANCE:
        - Eager loading de features con padres (jerarquía)
        - Eager loading de grupos con referencias cruzadas
        - Eager loading de relaciones de features
        - Reducción de N+1 queries a 1 query principal + N secondary queries

        Args:
            version_id: UUID de la versión
            include_resources: Si debe cargar los recursos asociados a features

        Returns:
            FeatureModelVersion con todas las relaciones cargadas, o None si no existe

        Performance:
            - Sin índices: ~50 queries en modelo 1000 features
            - Con índices + eager loading: ~3-5 queries
            - Esperado: 500ms -> 50-100ms
        """
        from sqlalchemy.orm import joinedload, contains_eager

        # Construir query con eager loading de todas las relaciones
        # Usar joinedload + contains_eager para optimizar jerarquía padre-hijo
        stmt = (
            select(FeatureModelVersion)
            .options(
                # Feature Model y Domain (carga inmediata)
                selectinload(FeatureModelVersion.feature_model).selectinload(
                    FeatureModel.domain
                ),
                # Features con jerarquía padre-hijo optimizada
                selectinload(FeatureModelVersion.features).selectinload(Feature.parent),
                selectinload(FeatureModelVersion.features).selectinload(
                    Feature.children
                ),
                # Features con tags
                selectinload(FeatureModelVersion.features).selectinload(Feature.tags),
                # Features con grupos
                selectinload(FeatureModelVersion.features).selectinload(Feature.group),
                selectinload(FeatureModelVersion.features).selectinload(
                    Feature.child_groups
                ),
                # Feature Relations con features de origen y destino
                selectinload(FeatureModelVersion.feature_relations).selectinload(
                    FeatureRelation.source_feature
                ),
                selectinload(FeatureModelVersion.feature_relations).selectinload(
                    FeatureRelation.target_feature
                ),
                # Feature Groups con parent feature
                (
                    selectinload(FeatureModelVersion.feature_groups).selectinload(
                        FeatureModelVersion.feature_groups.__dict__.get(
                            "parent_feature", None
                        )
                    )
                    if hasattr(FeatureModelVersion.feature_groups, "__dict__")
                    else selectinload(FeatureModelVersion.feature_groups)
                ),
                # Constraints
                selectinload(FeatureModelVersion.constraints),
                # Configurations
                selectinload(FeatureModelVersion.configurations),
            )
            .where(FeatureModelVersion.id == version_id)
        )

        # Si se deben incluir recursos, agregar carga de recursos en features
        if include_resources:
            stmt = stmt.options(
                selectinload(FeatureModelVersion.features).selectinload(
                    Feature.resource
                )
            )

        result = await self.session.execute(stmt)
        version = result.scalar_one_or_none()

        # Agregar métrica de caché para debugging
        if version:
            version._loaded_at = __import__("datetime").datetime.utcnow()
            version._eager_loaded = True

        return version

    async def get_statistics(self, version_id: uuid.UUID) -> dict[str, int] | None:
        """
        Calcular estadísticas de una versión de feature model de forma eficiente.

        Returns:
            Diccionario con las estadísticas o None si la versión no existe
        """
        from app.enums import FeatureType, FeatureRelationType, FeatureGroupType

        # Verificar que la versión existe
        version = await self.get(version_id)
        if not version:
            return None

        # Cargar la versión con todas las relaciones necesarias
        stmt = (
            select(FeatureModelVersion)
            .options(
                selectinload(FeatureModelVersion.features),
                selectinload(FeatureModelVersion.feature_relations),
                selectinload(FeatureModelVersion.feature_groups),
                selectinload(FeatureModelVersion.constraints),
                selectinload(FeatureModelVersion.configurations),
            )
            .where(FeatureModelVersion.id == version_id)
        )
        result = await self.session.execute(stmt)
        version = result.scalar_one_or_none()

        if not version:
            return None

        # Calcular estadísticas en memoria (más eficiente para conjuntos pequeños-medianos)
        features = version.features
        relations = version.feature_relations
        groups = version.feature_groups

        # Contar features por tipo
        mandatory_count = sum(1 for f in features if f.type == FeatureType.MANDATORY)
        optional_count = sum(1 for f in features if f.type == FeatureType.OPTIONAL)

        # Contar grupos por tipo
        xor_count = sum(
            1 for g in groups if g.group_type == FeatureGroupType.ALTERNATIVE
        )
        or_count = sum(1 for g in groups if g.group_type == FeatureGroupType.OR)

        # Contar relaciones por tipo
        requires_count = sum(
            1 for r in relations if r.type == FeatureRelationType.REQUIRED
        )
        excludes_count = sum(
            1 for r in relations if r.type == FeatureRelationType.EXCLUDES
        )

        # Calcular profundidad máxima del árbol
        max_depth = self._calculate_tree_depth(features)

        return {
            "total_features": len(features),
            "mandatory_features": mandatory_count,
            "optional_features": optional_count,
            "total_groups": len(groups),
            "xor_groups": xor_count,
            "or_groups": or_count,
            "total_relations": len(relations),
            "requires_relations": requires_count,
            "excludes_relations": excludes_count,
            "total_constraints": len(version.constraints),
            "total_configurations": len(version.configurations),
            "max_tree_depth": max_depth,
        }

    def _calculate_tree_depth(self, features: list[Feature]) -> int:
        """
        Calcular la profundidad máxima del árbol de features.

        Args:
            features: Lista de features

        Returns:
            Profundidad máxima (0 si solo hay raíz, 1 si hay un nivel, etc.)
        """
        if not features:
            return 0

        # Crear mapa de parent_id -> children
        children_map = {}
        root_features = []

        for feature in features:
            if feature.parent_id is None:
                root_features.append(feature)
            else:
                if feature.parent_id not in children_map:
                    children_map[feature.parent_id] = []
                children_map[feature.parent_id].append(feature)

        # Función recursiva para calcular profundidad
        def get_depth(feature_id: uuid.UUID, current_depth: int) -> int:
            if feature_id not in children_map:
                return current_depth

            max_child_depth = current_depth
            for child in children_map[feature_id]:
                child_depth = get_depth(child.id, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

            return max_child_depth

        # Calcular profundidad desde cada raíz
        max_depth = 0
        for root in root_features:
            depth = get_depth(root.id, 0)
            max_depth = max(max_depth, depth)

        return max_depth

    async def get_version_with_full_structure(
        self, version_id: uuid.UUID
    ) -> FeatureModelVersion | None:
        """
        Alias para get_complete_with_relations.
        Usado por el servicio de exportación.

        Args:
            version_id: UUID de la versión

        Returns:
            FeatureModelVersion con todas las relaciones cargadas, o None si no existe
        """
        return await self.get_complete_with_relations(
            version_id=version_id, include_resources=True
        )
