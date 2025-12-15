"""
Servicio para construir la estructura completa del árbol de Feature Model.
Optimizado para consulta única y renderizado en frontend.
"""

import uuid
from typing import Optional
from datetime import datetime

from app.models import (
    FeatureModelVersion,
    Feature,
    FeatureGroup,
)
from app.schemas.feature_model_complete import (
    FeatureModelCompleteResponse,
    FeatureModelInfo,
    FeatureModelVersionInfo,
    FeatureTreeNode,
    FeatureRelationInfo,
    ConstraintInfo,
    FeatureModelStatistics,
    ResponseMetadata,
    ResourceSummary,
    FeatureGroupInfo,
)
from app.enums import (
    FeatureType,
    FeatureGroupType,
    FeatureRelationType,
)


class FeatureModelTreeBuilder:
    """Constructor del árbol completo de Feature Model."""

    def __init__(self, version: FeatureModelVersion, include_resources: bool = True):
        self.version = version
        self.include_resources = include_resources
        self.start_time = datetime.utcnow()

    def build_complete_response(
        self,
        cached: bool = False,
        cache_expires_at: Optional[datetime] = None,
    ) -> FeatureModelCompleteResponse:
        """
        Construir la respuesta completa del feature model.

        Args:
            cached: Si la respuesta viene del caché
            cache_expires_at: Cuándo expira el caché

        Returns:
            FeatureModelCompleteResponse con toda la estructura
        """
        # 1. Información básica del feature model
        feature_model_info = self._build_feature_model_info()

        # 2. Información de la versión
        version_info = self._build_version_info()

        # 3. Construir árbol jerárquico
        tree = self._build_tree()

        # 4. Construir lista de relaciones
        relations = self._build_relations()

        # 5. Construir lista de constraints
        constraints = self._build_constraints()

        # 6. Calcular estadísticas
        statistics = self._calculate_statistics()

        # 7. Metadata de la respuesta
        processing_time = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        metadata = ResponseMetadata(
            cached=cached,
            cache_expires_at=cache_expires_at,
            generated_at=self.start_time,
            processing_time_ms=int(processing_time),
            version_status=self.version.status,
        )

        return FeatureModelCompleteResponse(
            feature_model=feature_model_info,
            version=version_info,
            tree=tree,
            relations=relations,
            constraints=constraints,
            statistics=statistics,
            metadata=metadata,
        )

    def _build_feature_model_info(self) -> FeatureModelInfo:
        """Construir información básica del feature model."""
        fm = self.version.feature_model
        return FeatureModelInfo(
            id=fm.id,
            name=fm.name,
            description=fm.description,
            domain_id=fm.domain_id,
            domain_name=fm.domain.name,
            owner_id=fm.owner_id,
            created_at=fm.created_at,
            updated_at=fm.updated_at,
            is_active=fm.is_active,
        )

    def _build_version_info(self) -> FeatureModelVersionInfo:
        """Construir información de la versión."""
        return FeatureModelVersionInfo(
            id=self.version.id,
            version_number=self.version.version_number,
            status=self.version.status,
            snapshot=self.version.snapshot,
            created_at=self.version.created_at,
        )

    def _build_tree(self) -> FeatureTreeNode:
        """
        Construir el árbol jerárquico completo de features.

        Returns:
            Nodo raíz con toda la estructura anidada
        """
        # Obtener todas las features de la versión
        features = self.version.features

        # Encontrar la feature raíz (parent_id = None)
        root_feature = next((f for f in features if f.parent_id is None), None)

        if not root_feature:
            # Si no hay raíz, crear un nodo vacío
            return FeatureTreeNode(
                id=uuid.uuid4(),
                name="Empty Model",
                type="MANDATORY",
                properties={},
                children=[],
                depth=0,
                is_leaf=True,
            )

        # Construir el árbol recursivamente
        return self._build_tree_node(root_feature, features, depth=0)

    def _build_tree_node(
        self, feature: Feature, all_features: list[Feature], depth: int = 0
    ) -> FeatureTreeNode:
        """
        Construir un nodo del árbol recursivamente.

        Args:
            feature: Feature actual
            all_features: Lista de todas las features para búsqueda de hijos
            depth: Profundidad actual en el árbol

        Returns:
            FeatureTreeNode con sus hijos anidados
        """
        # Obtener hijos de esta feature
        children_features = [f for f in all_features if f.parent_id == feature.id]

        # Construir nodos hijos recursivamente
        children_nodes = [
            self._build_tree_node(child, all_features, depth + 1)
            for child in sorted(children_features, key=lambda x: x.name)
        ]

        # Construir información del recurso si existe
        resource_summary = None
        if self.include_resources and feature.resource:
            resource = feature.resource
            resource_summary = ResourceSummary(
                id=resource.id,
                title=resource.title,
                type=resource.type,
                content_url_or_data=resource.content_url_or_data,
                language=resource.language,
                status=resource.status,
                duration_minutes=resource.duration_minutes,
            )

        # Construir información del grupo si existe
        group_info = None
        if feature.group:
            group = feature.group
            # Generar descripción legible del grupo
            group_description = self._generate_group_description(group)
            group_info = FeatureGroupInfo(
                id=group.id,
                group_type=group.group_type.value,
                min_cardinality=group.min_cardinality,
                max_cardinality=group.max_cardinality,
                description=group_description,
            )

        # Obtener nombres de tags
        tag_names = [tag.name for tag in feature.tags] if feature.tags else []

        # Construir el nodo
        return FeatureTreeNode(
            id=feature.id,
            name=feature.name,
            type=feature.type,
            properties=feature.properties or {},
            resource=resource_summary,
            tags=tag_names,
            group=group_info,
            children=children_nodes,
            depth=depth,
            is_leaf=len(children_nodes) == 0,
        )

    def _generate_group_description(self, group: FeatureGroup) -> str:
        """Generar descripción legible del grupo."""
        if group.group_type == FeatureGroupType.ALTERNATIVE:
            if group.min_cardinality == 1 and group.max_cardinality == 1:
                return "Debes elegir EXACTAMENTE UNA opción"
            else:
                return f"Debes elegir entre {group.min_cardinality} y {group.max_cardinality} opciones"
        elif group.group_type == FeatureGroupType.OR:
            if group.max_cardinality:
                return f"Debes elegir AL MENOS {group.min_cardinality} y COMO MÁXIMO {group.max_cardinality} opciones"
            else:
                return f"Debes elegir AL MENOS {group.min_cardinality} opción(es)"
        return ""

    def _build_relations(self) -> list[FeatureRelationInfo]:
        """Construir lista de relaciones entre features."""
        relations = []

        for relation in self.version.feature_relations:
            # Obtener nombres de las features
            source_name = (
                relation.source_feature.name if relation.source_feature else "Unknown"
            )
            target_name = (
                relation.target_feature.name if relation.target_feature else "Unknown"
            )

            # Generar descripción automática basada en el tipo de relación
            if relation.type == FeatureRelationType.REQUIRED:
                description = f"{source_name} requiere {target_name}"
            elif relation.type == FeatureRelationType.EXCLUDES:
                description = f"{source_name} excluye {target_name}"
            else:
                description = f"{source_name} → {target_name}"

            relations.append(
                FeatureRelationInfo(
                    id=relation.id,
                    type=relation.type.value,
                    source_feature_id=relation.source_feature_id,
                    source_feature_name=source_name,
                    target_feature_id=relation.target_feature_id,
                    target_feature_name=target_name,
                    description=description,
                )
            )

        return relations

    def _build_constraints(self) -> list[ConstraintInfo]:
        """Construir lista de constraints."""
        constraints = []

        for constraint in self.version.constraints:
            constraints.append(
                ConstraintInfo(
                    id=constraint.id,
                    description=constraint.description,
                    expr_text=constraint.expr_text,
                    expr_cnf=constraint.expr_cnf,
                )
            )

        return constraints

    def _calculate_statistics(self) -> FeatureModelStatistics:
        """Calcular estadísticas del feature model."""
        features = self.version.features

        # Contar por tipo
        mandatory_count = sum(1 for f in features if f.type == FeatureType.MANDATORY)
        optional_count = len(features) - mandatory_count

        # Contar grupos
        groups = self.version.feature_groups
        xor_count = sum(
            1 for g in groups if g.group_type == FeatureGroupType.ALTERNATIVE
        )
        or_count = sum(1 for g in groups if g.group_type == FeatureGroupType.OR)

        # Contar relaciones
        relations = self.version.feature_relations
        requires_count = sum(
            1 for r in relations if r.type == FeatureRelationType.REQUIRED
        )
        excludes_count = sum(
            1 for r in relations if r.type == FeatureRelationType.EXCLUDES
        )

        # Calcular profundidad máxima
        max_depth = self._calculate_max_depth(features)

        # Contar configuraciones
        configurations_count = len(self.version.configurations)

        return FeatureModelStatistics(
            total_features=len(features),
            mandatory_features=mandatory_count,
            optional_features=optional_count,
            total_groups=len(groups),
            xor_groups=xor_count,
            or_groups=or_count,
            total_relations=len(relations),
            requires_relations=requires_count,
            excludes_relations=excludes_count,
            total_constraints=len(self.version.constraints),
            total_configurations=configurations_count,
            max_tree_depth=max_depth,
        )

    def _calculate_max_depth(self, features: list[Feature]) -> int:
        """Calcular la profundidad máxima del árbol."""
        if not features:
            return 0

        # Encontrar la raíz
        root = next((f for f in features if f.parent_id is None), None)
        if not root:
            return 0

        # Calcular profundidad recursivamente
        return self._calculate_depth_recursive(root.id, features, 0)

    def _calculate_depth_recursive(
        self, feature_id: uuid.UUID, features: list[Feature], current_depth: int
    ) -> int:
        """Calcular profundidad recursivamente."""
        # Obtener hijos
        children = [f for f in features if f.parent_id == feature_id]

        if not children:
            return current_depth

        # Calcular profundidad de cada hijo
        depths = [
            self._calculate_depth_recursive(child.id, features, current_depth + 1)
            for child in children
        ]

        return max(depths)
