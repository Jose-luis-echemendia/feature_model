"""
Servicio para exportar Feature Models a diferentes formatos estándar.

Soporta exportación a:
- FeatureIDE XML: Formato compatible con FeatureIDE tool
- SPLOT XML: Formato compatible con SPLOT tool
- TVL: Textual Variability Language
- DIMACS: CNF format para SAT solvers
- JSON: Formato JSON simplificado
- UVL: Universal Variability Language
- DOT: Graphviz diagram format
- Mermaid: Mermaid diagram format
"""

import uuid
from typing import Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from app.models import (
    FeatureModelVersion,
    Feature,
    Constraint,
)
from app.enums import FeatureType, FeatureGroupType, FeatureRelationType, ExportFormat


class FeatureModelExportService:
    """Servicio para exportar Feature Models a diferentes formatos."""

    def __init__(self, version: FeatureModelVersion):
        """
        Inicializar el servicio de exportación.

        Args:
            version: La versión del Feature Model a exportar
        """
        self.version = version
        self.feature_model = version.feature_model

        # Crear mapeo de IDs para exportación
        self._build_id_mapping()

    def _build_id_mapping(self) -> None:
        """Construir mapeo entre UUIDs y IDs cortos para exportación."""
        self.uuid_to_int: dict[uuid.UUID, int] = {}
        self.int_to_uuid: dict[int, uuid.UUID] = {}

        # Mapear todas las features
        for idx, feature in enumerate(self.version.features, start=1):
            self.uuid_to_int[feature.id] = idx
            self.int_to_uuid[idx] = feature.id

    def export(self, format: ExportFormat) -> str:
        """
        Exportar el Feature Model al formato especificado.

        Args:
            format: Formato de exportación deseado

        Returns:
            String con el contenido exportado en el formato solicitado

        Raises:
            ValueError: Si el formato no está soportado
        """
        exporters = {
            ExportFormat.XML: self.export_to_featureide_xml,
            ExportFormat.SPLOT_XML: self.export_to_splot_xml,
            ExportFormat.TVL: self.export_to_tvl,
            ExportFormat.DIMACS: self.export_to_dimacs,
            ExportFormat.JSON: self.export_to_json,
            ExportFormat.UVL: self.export_to_uvl,
            ExportFormat.DOT: self.export_to_dot,
            ExportFormat.MERMAID: self.export_to_mermaid,
        }

        exporter = exporters.get(format)
        if not exporter:
            raise ValueError(f"Formato de exportación no soportado: {format}")

        return exporter()

    # ========================================================================
    # FEATUREIDE XML EXPORT
    # ========================================================================

    def export_to_featureide_xml(self) -> str:
        """
        Exportar a formato FeatureIDE XML.

        Este es el formato estándar usado por la herramienta FeatureIDE.
        Estructura:
        <featureModel>
            <properties/>
            <struct>
                <and name="Root" mandatory="true">
                    <feature name="Child1" mandatory="true"/>
                    <feature name="Child2" mandatory="false"/>
                    <alt name="Group1" mandatory="true">
                        <feature name="Option1"/>
                        <feature name="Option2"/>
                    </alt>
                </and>
            </struct>
            <constraints>
                <rule>
                    <imp>
                        <var>Feature1</var>
                        <var>Feature2</var>
                    </imp>
                </rule>
            </constraints>
        </featureModel>

        Returns:
            XML string formateado
        """
        # Crear elemento raíz
        root = Element("featureModel")

        # Agregar propiedades del modelo
        properties = SubElement(root, "properties")
        if self.feature_model.name:
            prop = SubElement(properties, "property")
            prop.set("key", "name")
            prop.set("value", self.feature_model.name)
        if self.feature_model.description:
            prop = SubElement(properties, "property")
            prop.set("key", "description")
            prop.set("value", self.feature_model.description)
        prop = SubElement(properties, "property")
        prop.set("key", "version")
        prop.set("value", str(self.version.version_number))

        # Construir estructura del árbol
        struct = SubElement(root, "struct")
        root_feature = self._get_root_feature()
        if root_feature:
            self._build_featureide_tree(struct, root_feature)

        # Agregar constraints
        if self.version.constraints:
            constraints = SubElement(root, "constraints")
            for constraint in self.version.constraints:
                self._build_featureide_constraint(constraints, constraint)

        # Formatear XML
        return self._prettify_xml(root)

    def _get_root_feature(self) -> Optional[Feature]:
        """Obtener la feature raíz del modelo."""
        for feature in self.version.features:
            if feature.parent_id is None:
                return feature
        return None

    def _build_featureide_tree(self, parent_element: Element, feature: Feature) -> None:
        """
        Construir árbol de features recursivamente para FeatureIDE XML.

        Args:
            parent_element: Elemento XML padre
            feature: Feature actual a procesar
        """
        # Determinar el tipo de elemento basado en el grupo
        children = [f for f in self.version.features if f.parent_id == feature.id]

        if feature.group:
            # Esta feature tiene un grupo, determinar el tipo
            group = feature.group
            if group.group_type == FeatureGroupType.ALTERNATIVE:
                element_type = "alt"  # XOR group
            elif group.group_type == FeatureGroupType.OR:
                element_type = "or"  # OR group
            else:
                element_type = "and"  # Default
        else:
            # Sin grupo, usar "and" por defecto
            element_type = "and" if children else "feature"

        # Crear elemento
        feature_element = SubElement(parent_element, element_type)
        feature_element.set("name", feature.name)

        # Establecer si es mandatory u optional
        if feature.type == FeatureType.MANDATORY:
            feature_element.set("mandatory", "true")
        else:
            feature_element.set("mandatory", "false")

        # Agregar propiedades adicionales si existen
        if feature.properties:
            for key, value in feature.properties.items():
                prop = SubElement(feature_element, "property")
                prop.set("key", str(key))
                prop.set("value", str(value))

        # Procesar hijos recursivamente
        for child in sorted(children, key=lambda x: x.name):
            self._build_featureide_tree(feature_element, child)

    def _build_featureide_constraint(
        self, constraints_element: Element, constraint: Constraint
    ) -> None:
        """
        Construir constraint en formato FeatureIDE XML.

        Args:
            constraints_element: Elemento XML de constraints
            constraint: Constraint a exportar
        """
        rule = SubElement(constraints_element, "rule")

        # TODO: Parsear constraint.expression y convertir a formato FeatureIDE
        # Por ahora, agregar como comentario
        comment = SubElement(rule, "description")
        comment.text = constraint.expression

    def _prettify_xml(self, element: Element) -> str:
        """
        Formatear XML con indentación.

        Args:
            element: Elemento XML raíz

        Returns:
            XML string formateado
        """
        rough_string = tostring(element, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    # ========================================================================
    # SPLOT XML EXPORT
    # ========================================================================

    def export_to_splot_xml(self) -> str:
        """
        Exportar a formato SPLOT XML.

        Formato usado por S.P.L.O.T (Software Product Lines Online Tools).
        Similar a FeatureIDE pero con algunas diferencias en la estructura.

        Returns:
            XML string en formato SPLOT
        """
        # TODO: Implementar formato SPLOT XML
        return "<!-- SPLOT XML format - TODO: Implementar -->"

    # ========================================================================
    # TVL EXPORT
    # ========================================================================

    def export_to_tvl(self) -> str:
        """
        Exportar a formato TVL (Textual Variability Language).

        TVL es un lenguaje textual para especificar feature models.
        Ejemplo:
        Root {
            mandatory:
                Feature1,
                Feature2;
            optional:
                Feature3;
            group allOf {
                Child1,
                Child2
            };
        }

        Returns:
            String en formato TVL
        """
        # TODO: Implementar formato TVL
        return "// TVL format - TODO: Implementar"

    # ========================================================================
    # DIMACS EXPORT
    # ========================================================================

    def export_to_dimacs(self) -> str:
        """
        Exportar a formato DIMACS CNF para SAT solvers.

        DIMACS es el formato estándar para problemas SAT.
        Usa el mapeo uuid_to_int del snapshot para asignar IDs.

        Returns:
            String en formato DIMACS CNF
        """
        clauses = []

        # 1. Constraint: Root feature debe estar presente
        root_feature = self._get_root_feature()
        if root_feature:
            root_id = self.uuid_to_int[root_feature.id]
            clauses.append([root_id])

        # 2. Para cada feature con parent: si parent está, hijos mandatory también
        for feature in self.version.features:
            if feature.parent_id and feature.type == FeatureType.MANDATORY:
                parent_id = self.uuid_to_int[feature.parent_id]
                feature_id = self.uuid_to_int[feature.id]
                # parent => child (equivalente a: -parent OR child)
                clauses.append([-parent_id, feature_id])

        # 3. Para grupos XOR (alternative): exactamente uno debe estar seleccionado
        for group in self.version.feature_groups:
            if group.group_type == FeatureGroupType.ALTERNATIVE:
                parent_feature = group.parent_feature
                if parent_feature:
                    parent_id = self.uuid_to_int[parent_feature.id]
                    children = [
                        f
                        for f in self.version.features
                        if f.parent_id == parent_feature.id
                    ]
                    children_ids = [self.uuid_to_int[f.id] for f in children]

                    # Si parent está, al menos uno de los hijos debe estar
                    clauses.append([-parent_id] + children_ids)

                    # Si parent está, no más de uno (pares excluyentes)
                    for i, id1 in enumerate(children_ids):
                        for id2 in children_ids[i + 1 :]:
                            # parent => not (child1 AND child2)
                            clauses.append([-parent_id, -id1, -id2])

        # 4. Relaciones REQUIRED y EXCLUDES
        for relation in self.version.feature_relations:
            source_id = self.uuid_to_int[relation.source_feature_id]
            target_id = self.uuid_to_int[relation.target_feature_id]

            if relation.type == FeatureRelationType.REQUIRED:
                # source => target (equivalente a: -source OR target)
                clauses.append([-source_id, target_id])
            elif relation.type == FeatureRelationType.EXCLUDES:
                # NOT (source AND target) (equivalente a: -source OR -target)
                clauses.append([-source_id, -target_id])

        # Generar formato DIMACS
        num_vars = len(self.uuid_to_int)
        num_clauses = len(clauses)

        lines = [
            f"c Feature Model: {self.feature_model.name}",
            f"c Version: {self.version.version_number}",
            f"c Variables: {num_vars}",
            f"c Clauses: {num_clauses}",
            f"p cnf {num_vars} {num_clauses}",
        ]

        # Agregar clauses
        for clause in clauses:
            lines.append(" ".join(map(str, clause)) + " 0")

        # Agregar mapeo de IDs
        lines.append("c")
        lines.append("c Variable mapping:")
        for feature in self.version.features:
            feature_id = self.uuid_to_int[feature.id]
            lines.append(f"c {feature_id}: {feature.name}")

        return "\n".join(lines)

    # ========================================================================
    # JSON EXPORT
    # ========================================================================

    def export_to_json(self) -> str:
        """
        Exportar a formato JSON simplificado.

        Returns:
            JSON string
        """
        import json

        root_feature = self._get_root_feature()

        data = {
            "name": self.feature_model.name,
            "description": self.feature_model.description,
            "version": self.version.version_number,
            "status": self.version.status.value,
            "tree": self._build_json_tree(root_feature) if root_feature else None,
            "relations": [
                {
                    "source": rel.source_feature.name,
                    "target": rel.target_feature.name,
                    "type": rel.type.value,
                }
                for rel in self.version.feature_relations
            ],
            "constraints": [
                {
                    "name": c.name,
                    "expression": c.expression,
                }
                for c in self.version.constraints
            ],
        }

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _build_json_tree(self, feature: Feature) -> dict:
        """Construir árbol en formato JSON recursivamente."""
        children = [f for f in self.version.features if f.parent_id == feature.id]

        node = {
            "name": feature.name,
            "type": feature.type.value,
            "properties": feature.properties or {},
        }

        if feature.group:
            node["group"] = {
                "type": feature.group.group_type.value,
                "min": feature.group.min_cardinality,
                "max": feature.group.max_cardinality,
            }

        if children:
            node["children"] = [
                self._build_json_tree(child)
                for child in sorted(children, key=lambda x: x.name)
            ]

        return node

    # ========================================================================
    # UVL EXPORT
    # ========================================================================

    def export_to_uvl(self) -> str:
        """
        Exportar a formato UVL (Universal Variability Language).

        UVL es un formato moderno y estandarizado para feature models.

        Formato UVL:
        namespace MyModel

        features
            Root
                mandatory
                    Feature1
                optional
                    Feature2
                alternative
                    Option1
                    Option2
                or
                    OrOption1
                    OrOption2

        constraints
            Feature1 => Feature2
            !Feature1 | Feature2

        Returns:
            String en formato UVL
        """
        lines = []

        # Namespace (usar nombre del modelo)
        namespace = self.feature_model.name.replace(" ", "_")
        lines.append(f"namespace {namespace}")
        lines.append("")

        # Sección de features
        lines.append("features")

        # Construir árbol de features
        root_feature = self._get_root_feature()
        if root_feature:
            self._build_uvl_tree(lines, root_feature, indent=1)

        lines.append("")

        # Sección de constraints
        if self.version.constraints or self.version.feature_relations:
            lines.append("constraints")

            # Agregar relaciones como constraints
            for relation in self.version.feature_relations:
                source_name = relation.source_feature.name.replace(" ", "_")
                target_name = relation.target_feature.name.replace(" ", "_")

                if relation.type == FeatureRelationType.REQUIRED:
                    # source requires target: source => target
                    lines.append(f"    {source_name} => {target_name}")
                elif relation.type == FeatureRelationType.EXCLUDES:
                    # source excludes target: !(source & target)
                    lines.append(f"    !({source_name} & {target_name})")

            # Agregar constraints adicionales
            for constraint in self.version.constraints:
                # Convertir expresión a formato UVL (simplificado)
                uvl_expr = self._convert_constraint_to_uvl(constraint.expression)
                lines.append(f"    {uvl_expr}")

        return "\n".join(lines)

    def _build_uvl_tree(
        self, lines: list[str], feature: Feature, indent: int = 0
    ) -> None:
        """
        Construir árbol de features recursivamente para formato UVL.

        Args:
            lines: Lista de líneas del documento UVL
            feature: Feature actual a procesar
            indent: Nivel de indentación
        """
        indent_str = "    " * indent
        feature_name = feature.name.replace(" ", "_")

        # Agregar nombre de la feature
        lines.append(f"{indent_str}{feature_name}")

        # Obtener hijos
        children = [f for f in self.version.features if f.parent_id == feature.id]

        if not children:
            return

        # Agrupar hijos por tipo y grupo
        mandatory_children = []
        optional_children = []
        alternative_children = []
        or_children = []

        for child in children:
            # Si el padre tiene un grupo, verificar el tipo de grupo
            if feature.group:
                if feature.group.group_type == FeatureGroupType.ALTERNATIVE:
                    alternative_children.append(child)
                elif feature.group.group_type == FeatureGroupType.OR:
                    or_children.append(child)
                else:
                    # Grupo AND: respetar tipo individual
                    if child.type == FeatureType.MANDATORY:
                        mandatory_children.append(child)
                    else:
                        optional_children.append(child)
            else:
                # Sin grupo: respetar tipo individual
                if child.type == FeatureType.MANDATORY:
                    mandatory_children.append(child)
                else:
                    optional_children.append(child)

        # Procesar mandatory children
        if mandatory_children:
            lines.append(f"{indent_str}    mandatory")
            for child in sorted(mandatory_children, key=lambda x: x.name):
                self._build_uvl_tree(lines, child, indent + 2)

        # Procesar optional children
        if optional_children:
            lines.append(f"{indent_str}    optional")
            for child in sorted(optional_children, key=lambda x: x.name):
                self._build_uvl_tree(lines, child, indent + 2)

        # Procesar alternative (XOR) children
        if alternative_children:
            lines.append(f"{indent_str}    alternative")
            for child in sorted(alternative_children, key=lambda x: x.name):
                self._build_uvl_tree(lines, child, indent + 2)

        # Procesar or children
        if or_children:
            lines.append(f"{indent_str}    or")
            for child in sorted(or_children, key=lambda x: x.name):
                self._build_uvl_tree(lines, child, indent + 2)

    def _convert_constraint_to_uvl(self, expression: str) -> str:
        """
        Convertir expresión de constraint a formato UVL.

        Operadores UVL:
        - & : AND
        - | : OR
        - => : IMPLIES
        - <=> : EQUIVALENCE
        - ! : NOT

        Args:
            expression: Expresión original del constraint

        Returns:
            Expresión en formato UVL
        """
        # Reemplazar nombres de features por identificadores válidos UVL
        uvl_expr = expression

        # Reemplazar operadores comunes a formato UVL
        replacements = {
            " AND ": " & ",
            " and ": " & ",
            " OR ": " | ",
            " or ": " | ",
            " IMPLIES ": " => ",
            " implies ": " => ",
            " => ": " => ",
            " NOT ": "!",
            " not ": "!",
            "NOT ": "!",
            "not ": "!",
        }

        for old, new in replacements.items():
            uvl_expr = uvl_expr.replace(old, new)

        # Reemplazar espacios en nombres de features
        for feature in self.version.features:
            if " " in feature.name:
                uvl_expr = uvl_expr.replace(
                    feature.name, feature.name.replace(" ", "_")
                )

        return uvl_expr

    # ========================================================================
    # DOT (Graphviz) EXPORT
    # ========================================================================

    def export_to_dot(self) -> str:
        """
        Exportar a formato DOT (Graphviz).

        Permite visualizar el feature model como un grafo.

        Returns:
            String en formato DOT
        """
        lines = [
            "digraph FeatureModel {",
            "  rankdir=TB;",
            "  node [shape=box, style=rounded];",
            f'  label="{self.feature_model.name}";',
            "  labelloc=t;",
            "",
        ]

        # Agregar nodos
        for feature in self.version.features:
            feature_id = self.uuid_to_int[feature.id]
            label = feature.name

            # Determinar estilo según tipo
            if feature.type == FeatureType.MANDATORY:
                style = 'fillcolor=lightblue, style="rounded,filled"'
            else:
                style = 'fillcolor=white, style="rounded,filled,dashed"'

            lines.append(f'  f{feature_id} [label="{label}", {style}];')

        lines.append("")

        # Agregar edges (relaciones parent-child)
        for feature in self.version.features:
            if feature.parent_id:
                parent_id = self.uuid_to_int[feature.parent_id]
                feature_id = self.uuid_to_int[feature.id]
                lines.append(f"  f{parent_id} -> f{feature_id};")

        # Agregar relaciones (requires, excludes)
        for relation in self.version.feature_relations:
            source_id = self.uuid_to_int[relation.source_feature_id]
            target_id = self.uuid_to_int[relation.target_feature_id]

            if relation.type == FeatureRelationType.REQUIRED:
                lines.append(
                    f'  f{source_id} -> f{target_id} [style=dashed, color=green, label="requires"];'
                )
            elif relation.type == FeatureRelationType.EXCLUDES:
                lines.append(
                    f'  f{source_id} -> f{target_id} [style=dashed, color=red, label="excludes", dir=none];'
                )

        lines.append("}")

        return "\n".join(lines)

    # ========================================================================
    # MERMAID EXPORT
    # ========================================================================

    def export_to_mermaid(self) -> str:
        """
        Exportar a formato Mermaid para diagramas.

        Mermaid permite visualizar el feature model en Markdown y web.

        Returns:
            String en formato Mermaid
        """
        lines = [
            "graph TD",
        ]

        # Agregar nodos con estilos
        for feature in self.version.features:
            feature_id = self.uuid_to_int[feature.id]
            label = feature.name

            # Determinar forma según tipo
            if feature.type == FeatureType.MANDATORY:
                lines.append(f'  f{feature_id}["{label}"]')
            else:
                lines.append(f'  f{feature_id}("{label}")')

        lines.append("")

        # Agregar conexiones parent-child
        for feature in self.version.features:
            if feature.parent_id:
                parent_id = self.uuid_to_int[feature.parent_id]
                feature_id = self.uuid_to_int[feature.id]

                if feature.type == FeatureType.MANDATORY:
                    lines.append(f"  f{parent_id} --> f{feature_id}")
                else:
                    lines.append(f"  f{parent_id} -.-> f{feature_id}")

        # Agregar relaciones
        for relation in self.version.feature_relations:
            source_id = self.uuid_to_int[relation.source_feature_id]
            target_id = self.uuid_to_int[relation.target_feature_id]

            if relation.type == FeatureRelationType.REQUIRED:
                lines.append(f"  f{source_id} ==>|requires| f{target_id}")
            elif relation.type == FeatureRelationType.EXCLUDES:
                lines.append(f"  f{source_id} -.->|excludes| f{target_id}")

        # Agregar estilos
        lines.extend(
            [
                "",
                "  classDef mandatory fill:#e1f5ff,stroke:#01579b,stroke-width:2px",
                "  classDef optional fill:#fff,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5",
            ]
        )

        return "\n".join(lines)
