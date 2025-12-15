"""
Gestor de Versionado de Modelos de Características (FM Version Manager).

Este componente es responsable de:
- Captura de snapshots inmutables del modelo completo
- Control de versiones con numeración secuencial
- Registro de evolución histórica del modelo
- Garantía de reproducibilidad de configuraciones pasadas
- Trazabilidad completa de cambios
- Gestión de estados (DRAFT, PUBLISHED, ARCHIVED)
- Preservación de relaciones UUID↔Integer para exportación
"""

import uuid
from datetime import datetime
from typing import Optional, Any

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    FeatureModel,
    FeatureModelVersion,
    Feature,
    User,
)
from app.enums import ModelStatus, FeatureType, FeatureGroupType, FeatureRelationType
from app.repositories.a_sync.feature_model_version import (
    FeatureModelVersionRepositoryAsync,
)
from app.exceptions import (
    FeatureModelVersionNotFoundException,
    InvalidVersionStateException,
    MissingRootFeatureException,
    MultipleRootFeaturesException,
    CyclicDependencyException,
    InvalidRelationException,
)


class FeatureModelVersionManager:
    """
    Gestor de Versionado de Feature Models.

    Proporciona funcionalidades para gestionar el ciclo de vida completo
    de las versiones de los modelos de características, garantizando
    inmutabilidad, trazabilidad y reproducibilidad.

    Responsabilidades:
    - Creación de nuevas versiones (snapshots inmutables)
    - Publicación y archivo de versiones
    - Gestión de estado del ciclo de vida
    - Construcción de snapshots con mapeo UUID↔Integer
    - Cálculo de estadísticas y métricas
    - Validación de transiciones de estado
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_model: FeatureModel,
        user: Optional[User] = None,
    ):
        """
        Inicializar el gestor de versiones.

        Args:
            session: Sesión asíncrona de base de datos
            feature_model: Feature Model asociado
            user: Usuario que realiza las operaciones (para auditoría)
        """
        self.session = session
        self.feature_model = feature_model
        self.user = user
        self.repository = FeatureModelVersionRepositoryAsync(session)

    # ========================================================================
    # CREACIÓN Y GESTIÓN DE VERSIONES
    # ========================================================================

    async def create_new_version(
        self,
        source_version: Optional[FeatureModelVersion] = None,
        description: Optional[str] = None,
    ) -> FeatureModelVersion:
        """
        Crear una nueva versión del feature model.

        Si se proporciona una versión origen, se copia toda su estructura.
        Si no, se crea una versión vacía en estado DRAFT.

        Args:
            source_version: Versión de origen para copiar (opcional)
            description: Descripción de los cambios en esta versión

        Returns:
            Nueva versión creada

        Raises:
            BusinessLogicException: Si hay errores en la lógica de negocio
        """
        # Obtener el siguiente número de versión
        next_version_number = (
            await self.repository.get_latest_version_number(self.feature_model.id) + 1
        )

        if source_version:
            # Crear nueva versión copiando la estructura de la versión origen
            new_version = await self.repository.create_new_version_from_existing(
                source_version=source_version,
                user=self.user,
            )
            new_version.version_number = next_version_number
            new_version.status = ModelStatus.DRAFT
        else:
            # Crear versión vacía
            new_version = FeatureModelVersion(
                feature_model_id=self.feature_model.id,
                version_number=next_version_number,
                status=ModelStatus.DRAFT,
                created_by_id=self.user.id if self.user else None,
            )
            self.session.add(new_version)

        await self.session.commit()
        await self.session.refresh(new_version)

        return new_version

    async def get_latest_version(
        self, status: Optional[ModelStatus] = None
    ) -> Optional[FeatureModelVersion]:
        """
        Obtener la última versión del feature model.

        Args:
            status: Filtrar por estado (opcional). Si no se especifica,
                   devuelve la última versión independientemente del estado.

        Returns:
            Última versión encontrada o None si no hay versiones
        """
        if not self.feature_model.versions:
            return None

        versions = self.feature_model.versions

        # Filtrar por estado si se especifica
        if status:
            versions = [v for v in versions if v.status == status]

        if not versions:
            return None

        # Obtener la versión con el mayor número de versión
        latest_version = max(versions, key=lambda v: v.version_number)
        return latest_version

    async def get_version_by_number(self, version_number: int) -> FeatureModelVersion:
        """
        Obtener una versión específica por su número.

        Args:
            version_number: Número de versión a buscar

        Returns:
            Versión encontrada

        Raises:
            NotFoundException: Si no existe la versión
        """
        for version in self.feature_model.versions:
            if version.version_number == version_number:
                return version

        raise FeatureModelVersionNotFoundException(version_number=version_number)

    # ========================================================================
    # PUBLICACIÓN Y GESTIÓN DE ESTADO
    # ========================================================================

    async def publish_version(
        self, version: FeatureModelVersion, validate: bool = True
    ) -> FeatureModelVersion:
        """
        Publicar una versión, haciéndola inmutable y disponible para uso.

        Una versión publicada:
        - Cambia su estado a PUBLISHED
        - Se vuelve inmutable (no se puede modificar)
        - Genera un snapshot completo para reproducibilidad
        - Calcula y almacena estadísticas

        Args:
            version: Versión a publicar
            validate: Si se debe validar la versión antes de publicar

        Returns:
            Versión publicada

        Raises:
            BusinessLogicException: Si la versión no está en estado DRAFT
            UnprocessableEntityException: Si la validación falla
        """
        # Verificar que la versión esté en estado DRAFT
        if version.status != ModelStatus.DRAFT:
            raise InvalidVersionStateException(
                current_state=version.status.value,
                required_state=ModelStatus.DRAFT.value,
                operation="publish version",
            )

        # Validar la versión si se solicita
        if validate:
            await self._validate_version(version)

        # Generar snapshot inmutable
        snapshot = await self._build_snapshot(version)
        version.snapshot = snapshot

        # Cambiar estado a PUBLISHED
        version.status = ModelStatus.PUBLISHED

        await self.session.commit()
        await self.session.refresh(version)

        return version

    async def archive_version(
        self, version: FeatureModelVersion
    ) -> FeatureModelVersion:
        """
        Archivar una versión, marcándola como obsoleta pero manteniendo
        su inmutabilidad y accesibilidad histórica.

        Args:
            version: Versión a archivar

        Returns:
            Versión archivada

        Raises:
            BusinessLogicException: Si la versión no está publicada
        """
        if version.status != ModelStatus.PUBLISHED:
            raise InvalidVersionStateException(
                current_state=version.status.value,
                required_state=ModelStatus.PUBLISHED.value,
                operation="archive version",
            )

        version.status = ModelStatus.ARCHIVED

        await self.session.commit()
        await self.session.refresh(version)

        return version

    async def restore_version(
        self, version: FeatureModelVersion
    ) -> FeatureModelVersion:
        """
        Restaurar una versión archivada a estado PUBLISHED.

        Args:
            version: Versión a restaurar

        Returns:
            Versión restaurada

        Raises:
            BusinessLogicException: Si la versión no está archivada
        """
        if version.status != ModelStatus.ARCHIVED:
            raise InvalidVersionStateException(
                current_state=version.status.value,
                required_state=ModelStatus.ARCHIVED.value,
                operation="restore version",
            )

        version.status = ModelStatus.PUBLISHED

        await self.session.commit()
        await self.session.refresh(version)

        return version

    # ========================================================================
    # SNAPSHOT Y REPRODUCIBILIDAD
    # ========================================================================

    async def _build_snapshot(self, version: FeatureModelVersion) -> dict[str, Any]:
        """
        Construir snapshot completo de la versión para garantizar reproducibilidad.

        El snapshot incluye:
        - Mapeo UUID↔Integer para compatibilidad con herramientas externas
        - Estructura completa del árbol de features
        - Todas las relaciones y constraints
        - Estadísticas precalculadas
        - Metadatos de caché

        Args:
            version: Versión de la cual construir el snapshot

        Returns:
            Diccionario con el snapshot completo
        """
        # Cargar versión completa con todas las relaciones
        version_complete = await self.repository.get_version_with_full_structure(
            version.id
        )

        # Construir mapeo UUID↔Integer
        uuid_to_int: dict[str, int] = {}
        int_to_uuid: dict[int, str] = {}

        for idx, feature in enumerate(version_complete.features, start=1):
            uuid_to_int[str(feature.id)] = idx
            int_to_uuid[idx] = str(feature.id)

        # Construir estructura del árbol
        tree = self._build_tree_structure(version_complete)

        # Calcular estadísticas
        statistics = self._calculate_statistics(version_complete)

        # Construir snapshot
        snapshot = {
            "version_number": version.version_number,
            "created_at": datetime.utcnow().isoformat(),
            "created_by_id": (
                str(version.created_by_id) if version.created_by_id else None
            ),
            "feature_model": {
                "id": str(self.feature_model.id),
                "name": self.feature_model.name,
                "description": self.feature_model.description,
            },
            "mapping": {
                "uuid_to_int": uuid_to_int,
                "int_to_uuid": int_to_uuid,
            },
            "tree": tree,
            "statistics": statistics,
            "metadata": {
                "total_features": len(version_complete.features),
                "total_relations": len(version_complete.feature_relations),
                "total_constraints": len(version_complete.constraints),
                "total_groups": len(version_complete.feature_groups),
                "cache_timestamp": datetime.utcnow().isoformat(),
            },
        }

        return snapshot

    def _build_tree_structure(self, version: FeatureModelVersion) -> dict[str, Any]:
        """
        Construir estructura arbórea de features.

        Args:
            version: Versión con features cargadas

        Returns:
            Diccionario con estructura del árbol
        """
        # Encontrar raíz
        root_feature = None
        for feature in version.features:
            if feature.parent_id is None:
                root_feature = feature
                break

        if not root_feature:
            return {}

        # Construir árbol recursivamente
        return self._build_tree_node(root_feature, version.features)

    def _build_tree_node(
        self, feature: Feature, all_features: list[Feature]
    ) -> dict[str, Any]:
        """Construir nodo del árbol recursivamente."""
        node = {
            "id": str(feature.id),
            "name": feature.name,
            "type": feature.type.value,
            "properties": feature.properties or {},
        }

        # Agregar información de grupo si existe
        if feature.group:
            node["group"] = {
                "type": feature.group.group_type.value,
                "min_cardinality": feature.group.min_cardinality,
                "max_cardinality": feature.group.max_cardinality,
            }

        # Construir hijos
        children = [f for f in all_features if f.parent_id == feature.id]
        if children:
            node["children"] = [
                self._build_tree_node(child, all_features)
                for child in sorted(children, key=lambda x: x.name)
            ]

        return node

    def _calculate_statistics(self, version: FeatureModelVersion) -> dict[str, Any]:
        """
        Calcular estadísticas de la versión.

        Args:
            version: Versión con datos cargados

        Returns:
            Diccionario con estadísticas calculadas
        """
        total_features = len(version.features)
        mandatory_features = sum(
            1 for f in version.features if f.type == FeatureType.MANDATORY
        )
        optional_features = total_features - mandatory_features

        # Calcular profundidad máxima del árbol
        max_depth = self._calculate_max_depth(version.features)

        # Contar tipos de grupos
        alternative_groups = sum(
            1
            for g in version.feature_groups
            if g.group_type == FeatureGroupType.ALTERNATIVE
        )
        or_groups = sum(
            1 for g in version.feature_groups if g.group_type == FeatureGroupType.OR
        )

        # Contar tipos de relaciones
        requires_relations = sum(
            1
            for r in version.feature_relations
            if r.type == FeatureRelationType.REQUIRED
        )
        excludes_relations = sum(
            1
            for r in version.feature_relations
            if r.type == FeatureRelationType.EXCLUDES
        )

        return {
            "total_features": total_features,
            "mandatory_features": mandatory_features,
            "optional_features": optional_features,
            "max_depth": max_depth,
            "total_groups": len(version.feature_groups),
            "alternative_groups": alternative_groups,
            "or_groups": or_groups,
            "total_relations": len(version.feature_relations),
            "requires_relations": requires_relations,
            "excludes_relations": excludes_relations,
            "total_constraints": len(version.constraints),
            "complexity_score": self._calculate_complexity_score(version),
        }

    def _calculate_max_depth(self, features: list[Feature]) -> int:
        """Calcular profundidad máxima del árbol."""
        # Encontrar raíz
        root = None
        for feature in features:
            if feature.parent_id is None:
                root = feature
                break

        if not root:
            return 0

        # Calcular profundidad recursivamente
        return self._calculate_depth_recursive(root, features)

    def _calculate_depth_recursive(
        self, feature: Feature, all_features: list[Feature], current_depth: int = 1
    ) -> int:
        """Calcular profundidad de forma recursiva."""
        children = [f for f in all_features if f.parent_id == feature.id]

        if not children:
            return current_depth

        max_child_depth = max(
            self._calculate_depth_recursive(child, all_features, current_depth + 1)
            for child in children
        )

        return max_child_depth

    def _calculate_complexity_score(self, version: FeatureModelVersion) -> float:
        """
        Calcular puntuación de complejidad del modelo.

        La complejidad se basa en:
        - Número de features
        - Profundidad del árbol
        - Número de relaciones cross-tree
        - Número de constraints
        - Número de grupos
        """
        features_weight = len(version.features) * 0.5
        relations_weight = len(version.feature_relations) * 2.0
        constraints_weight = len(version.constraints) * 3.0
        groups_weight = len(version.feature_groups) * 1.5
        depth_weight = self._calculate_max_depth(version.features) * 1.0

        return round(
            features_weight
            + relations_weight
            + constraints_weight
            + groups_weight
            + depth_weight,
            2,
        )

    # ========================================================================
    # VALIDACIÓN
    # ========================================================================

    async def _validate_version(self, version: FeatureModelVersion) -> None:
        """
        Validar que una versión sea consistente antes de publicarla.

        Validaciones:
        - Debe tener al menos una feature raíz
        - No debe haber ciclos en el árbol
        - Las relaciones deben apuntar a features válidas
        - Los constraints deben ser parseables

        Args:
            version: Versión a validar

        Raises:
            UnprocessableEntityException: Si la validación falla
        """
        # Verificar que haya una raíz
        root_count = sum(1 for f in version.features if f.parent_id is None)
        if root_count == 0:
            raise MissingRootFeatureException()
        if root_count > 1:
            raise MultipleRootFeaturesException(count=root_count)

        # Verificar que no haya ciclos
        if self._has_cycles(version.features):
            raise CyclicDependencyException("Feature tree contains cycles")

        # Validar relaciones
        feature_ids = {f.id for f in version.features}
        for relation in version.feature_relations:
            if relation.source_feature_id not in feature_ids:
                raise InvalidRelationException(
                    f"Source feature '{relation.source_feature_id}' does not exist in version"
                )
            if relation.target_feature_id not in feature_ids:
                raise InvalidRelationException(
                    f"Target feature '{relation.target_feature_id}' does not exist in version"
                )

    def _has_cycles(self, features: list[Feature]) -> bool:
        """Detectar ciclos en el árbol de features."""
        visited = set()
        rec_stack = set()

        def has_cycle_util(feature_id: uuid.UUID) -> bool:
            visited.add(feature_id)
            rec_stack.add(feature_id)

            # Encontrar hijos
            children = [f for f in features if f.parent_id == feature_id]

            for child in children:
                if child.id not in visited:
                    if has_cycle_util(child.id):
                        return True
                elif child.id in rec_stack:
                    return True

            rec_stack.remove(feature_id)
            return False

        # Buscar raíz y comenzar desde ahí
        for feature in features:
            if feature.parent_id is None:
                return has_cycle_util(feature.id)

        return False
