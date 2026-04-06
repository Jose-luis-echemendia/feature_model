"""
Servicio para importar UVL y crear estructura de Feature Model.
Fases 1-6: parseo, estructura base, constraints simples, validaciones,
sincronización y diff.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.enums import FeatureGroupType, FeatureType, FeatureRelationType
from app.exceptions import BusinessLogicException
from app.models import (
    Feature,
    FeatureGroup,
    FeatureModel,
    FeatureModelVersion,
    FeatureRelation,
    Constraint,
    User,
)
from app.services.feature_model.fm_version_manager import FeatureModelVersionManager


@dataclass
class ParsedChild:
    name: str
    relation_type: str
    group_type: Optional[str] = None


@dataclass
class ParsedNode:
    name: str
    children: List[ParsedChild]


class UVLParseError(BusinessLogicException):
    """Error de parseo UVL."""

    def __init__(self, reason: str):
        super().__init__(detail=f"UVL parse error: {reason}")


class FeatureModelUVLImporter:
    """Importador UVL -> estructura base."""

    def __init__(self, session: AsyncSession, feature_model: FeatureModel, user: User):
        self.session = session
        self.feature_model = feature_model
        self.user = user

    @classmethod
    def validate_uvl_only(cls, uvl_content: str) -> dict:
        """Valida UVL sin persistir: estructura, cardinalidad y constraints simples."""
        parser = cls.__new__(cls)
        parsed, constraints = parser._parse_uvl(uvl_content)
        parser._validate_parsed_structure(parsed)
        parser._validate_constraints(constraints, parsed)
        root = parser._find_root(parsed)
        return {
            "is_valid": True,
            "root": root,
            "features": len(parsed),
            "constraints": len(constraints),
        }

    async def apply_uvl(self, uvl_content: str) -> FeatureModelVersion:
        parsed, constraints = self._parse_uvl(uvl_content)
        root_name = self._find_root(parsed)
        self._validate_parsed_structure(parsed)
        self._validate_constraints(constraints, parsed)

        manager = FeatureModelVersionManager(
            session=self.session,
            feature_model=self.feature_model,
            user=self.user,
        )
        new_version = await manager.create_new_version(source_version=None)

        name_to_id: Dict[str, str] = {}

        # Crear root
        root_feature = Feature(
            name=root_name,
            type=FeatureType.MANDATORY,
            feature_model_version_id=new_version.id,
            parent_id=None,
            created_by_id=self.user.id,
        )
        self.session.add(root_feature)
        await self.session.flush()
        name_to_id[self._normalize_name(root_name)] = str(root_feature.id)

        # Crear resto del árbol
        queue = [root_name]
        while queue:
            current = queue.pop(0)
            parent_id = name_to_id[self._normalize_name(current)]
            node = parsed[current]
            for child in node.children:
                if self._normalize_name(child.name) in name_to_id:
                    raise UVLParseError(reason=f"Duplicate feature name '{child.name}'")
                feature_type = (
                    FeatureType.MANDATORY
                    if child.relation_type == "mandatory"
                    else FeatureType.OPTIONAL
                )
                new_feature = Feature(
                    name=child.name,
                    type=feature_type,
                    feature_model_version_id=new_version.id,
                    parent_id=parent_id,
                    created_by_id=self.user.id,
                )
                self.session.add(new_feature)
                await self.session.flush()
                name_to_id[self._normalize_name(child.name)] = str(new_feature.id)
                queue.append(child.name)

        # Crear grupos (alternative/or)
        parent_to_group: Dict[str, FeatureGroup] = {}
        for parent_name, node in parsed.items():
            group_children = [c for c in node.children if c.group_type]
            if not group_children:
                continue

            group_type = group_children[0].group_type
            if group_type not in {"alternative", "or"}:
                continue

            parent_id = name_to_id[self._normalize_name(parent_name)]
            min_card = 1
            max_card = 1 if group_type == "alternative" else None
            group = FeatureGroup(
                group_type=(
                    FeatureGroupType.ALTERNATIVE
                    if group_type == "alternative"
                    else FeatureGroupType.OR
                ),
                parent_feature_id=parent_id,
                min_cardinality=min_card,
                max_cardinality=max_card,
                feature_model_version_id=new_version.id,
                created_by_id=self.user.id,
            )
            self.session.add(group)
            await self.session.flush()
            parent_to_group[parent_name] = group

            # Asignar group_id a hijos del grupo
            for child in group_children:
                child_id = name_to_id[self._normalize_name(child.name)]
                feature_stmt = await self.session.get(Feature, child_id)
                if feature_stmt:
                    feature_stmt.group_id = group.id
                    self.session.add(feature_stmt)

        # Crear relaciones/constraints simples
        for raw in constraints:
            parsed_constraint = self._parse_constraint(raw, name_to_id)
            if parsed_constraint is None:
                new_constraint = Constraint(
                    description=None,
                    expr_text=raw,
                    feature_model_version_id=new_version.id,
                    created_by_id=self.user.id,
                )
                self.session.add(new_constraint)
                continue

            ctype, left_id, right_id = parsed_constraint
            if ctype == "requires":
                relation = FeatureRelation(
                    type=FeatureRelationType.REQUIRED,
                    source_feature_id=left_id,
                    target_feature_id=right_id,
                    feature_model_version_id=new_version.id,
                    created_by_id=self.user.id,
                )
                self.session.add(relation)
            elif ctype == "excludes":
                relation = FeatureRelation(
                    type=FeatureRelationType.EXCLUDES,
                    source_feature_id=left_id,
                    target_feature_id=right_id,
                    feature_model_version_id=new_version.id,
                    created_by_id=self.user.id,
                )
                self.session.add(relation)

        # Persistir UVL en la nueva versión
        new_version.uvl_content = uvl_content.strip()
        self.session.add(new_version)
        await self.session.commit()
        await self.session.refresh(new_version)
        return new_version

    def diff_uvl(self, uvl_content: str, version: FeatureModelVersion) -> dict:
        """Comparar UVL contra estructura actual y devolver diferencias."""
        parsed, constraints = self._parse_uvl(uvl_content)
        self._validate_parsed_structure(parsed)

        uvl_features = {self._normalize_name(name) for name in parsed.keys()}
        uvl_relations = self._extract_uvl_relations(constraints, parsed)
        uvl_constraints = self._extract_uvl_constraints(constraints, parsed)

        structure_features = {self._normalize_name(f.name) for f in version.features}
        structure_relations = {
            (
                self._normalize_name(rel.source_feature.name),
                self._normalize_name(rel.target_feature.name),
                rel.type.value,
            )
            for rel in version.feature_relations
        }
        structure_constraints = {
            c.expr_text.strip() for c in version.constraints if c.expr_text
        }

        return {
            "features_added": sorted(uvl_features - structure_features),
            "features_removed": sorted(structure_features - uvl_features),
            "relations_added": sorted(uvl_relations - structure_relations),
            "relations_removed": sorted(structure_relations - uvl_relations),
            "constraints_added": sorted(uvl_constraints - structure_constraints),
            "constraints_removed": sorted(structure_constraints - uvl_constraints),
        }

    def _parse_uvl(self, uvl_content: str) -> tuple[Dict[str, ParsedNode], List[str]]:
        lines = [line.rstrip("\n") for line in uvl_content.splitlines()]
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("//") or stripped.startswith("#"):
                continue
            cleaned.append(line)

        in_features = False
        in_constraints = False
        parsed: Dict[str, ParsedNode] = {}
        constraints: List[str] = []

        stack: List[dict] = []

        for raw in cleaned:
            text = raw.strip()
            if text.lower().startswith("namespace "):
                continue
            if text == "features":
                in_features = True
                in_constraints = False
                stack = []
                continue
            if text == "constraints":
                in_features = False
                in_constraints = True
                continue
            if in_constraints:
                constraints.append(text)
                continue
            if not in_features:
                continue

            indent = len(raw) - len(raw.lstrip(" "))
            if indent % 4 != 0:
                raise UVLParseError(reason=f"Invalid indentation: '{raw}'")
            level = indent // 4

            while stack and level <= stack[-1]["level"]:
                stack.pop()

            if text in {"mandatory", "optional", "alternative", "or"}:
                parent = next(
                    (item for item in reversed(stack) if item["kind"] == "feature"),
                    None,
                )
                if not parent:
                    raise UVLParseError(reason=f"Group '{text}' without parent")
                stack.append(
                    {
                        "kind": "group",
                        "level": level,
                        "relation_type": (
                            text if text in {"mandatory", "optional"} else None
                        ),
                        "group_type": text if text in {"alternative", "or"} else None,
                        "parent": parent["name"],
                    }
                )
                continue

            parent = next(
                (item for item in reversed(stack) if item["kind"] == "feature"),
                None,
            )
            group_ctx = stack[-1] if stack and stack[-1]["kind"] == "group" else None
            relation_type = group_ctx.get("relation_type") if group_ctx else "mandatory"
            group_type = group_ctx.get("group_type") if group_ctx else None
            parent_name = parent["name"] if parent else None

            if text not in parsed:
                parsed[text] = ParsedNode(name=text, children=[])

            if parent_name:
                if parent_name not in parsed:
                    parsed[parent_name] = ParsedNode(name=parent_name, children=[])
                parsed[parent_name].children.append(
                    ParsedChild(
                        name=text,
                        relation_type=relation_type or "optional",
                        group_type=group_type,
                    )
                )

            stack.append({"kind": "feature", "level": level, "name": text})

        if not parsed:
            raise UVLParseError(reason="No features parsed")
        return parsed, constraints

    def _find_root(self, parsed: Dict[str, ParsedNode]) -> str:
        parents = {child.name for node in parsed.values() for child in node.children}
        roots = [name for name in parsed.keys() if name not in parents]
        if len(roots) != 1:
            raise UVLParseError(reason=f"Expected single root, found {len(roots)}")
        return roots[0]

    def _validate_parsed_structure(self, parsed: Dict[str, ParsedNode]) -> None:
        """Validaciones de estructura: ciclos, grupos, cardinalidad."""
        # Validar ciclos
        graph = {
            name: [child.name for child in node.children]
            for name, node in parsed.items()
        }
        visited: set[str] = set()
        stack: set[str] = set()

        def dfs(node: str) -> None:
            if node in stack:
                raise UVLParseError(reason=f"Cycle detected at '{node}'")
            if node in visited:
                return
            visited.add(node)
            stack.add(node)
            for child in graph.get(node, []):
                if child not in graph:
                    raise UVLParseError(reason=f"Undefined feature '{child}'")
                dfs(child)
            stack.remove(node)

        for node in graph.keys():
            if node not in visited:
                dfs(node)

        # Validar grupos
        for parent_name, node in parsed.items():
            group_children = [c for c in node.children if c.group_type]
            if not group_children:
                continue

            group_types = {c.group_type for c in group_children}
            if len(group_types) > 1:
                raise UVLParseError(reason=f"Mixed group types under '{parent_name}'")

            group_type = group_children[0].group_type
            count = len(group_children)
            if group_type == "alternative" and count < 2:
                raise UVLParseError(
                    reason=f"Alternative group under '{parent_name}' requires >= 2 children"
                )
            if group_type == "or" and count < 1:
                raise UVLParseError(
                    reason=f"OR group under '{parent_name}' requires >= 1 child"
                )

    def _validate_constraints(
        self, constraints: List[str], parsed: Dict[str, ParsedNode]
    ) -> None:
        """Validar constraints simples: referencias a features existentes."""
        name_to_id = {
            self._normalize_name(name): self._normalize_name(name)
            for name in parsed.keys()
        }
        for raw in constraints:
            parsed_constraint = self._parse_constraint(raw, name_to_id)
            if parsed_constraint is None:
                continue
            _, left_id, right_id = parsed_constraint
            if left_id not in name_to_id.values():
                raise UVLParseError(
                    reason=f"Unknown feature in constraint: '{left_id}'"
                )
            if right_id not in name_to_id.values():
                raise UVLParseError(
                    reason=f"Unknown feature in constraint: '{right_id}'"
                )

    def _parse_constraint(
        self, raw: str, name_to_id: Dict[str, str]
    ) -> Optional[tuple[str, str, str]]:
        """Parsea constraints simples: A => B, !(A & B), !A | !B."""
        expr = raw.strip()
        if "=>" in expr:
            left, right = expr.split("=>", 1)
            left_id = self._resolve_name(left, name_to_id)
            right_id = self._resolve_name(right, name_to_id)
            return "requires", left_id, right_id

        if expr.startswith("!(") and expr.endswith(")") and "&" in expr:
            inner = expr[2:-1]
            left, right = inner.split("&", 1)
            left_id = self._resolve_name(left, name_to_id)
            right_id = self._resolve_name(right, name_to_id)
            return "excludes", left_id, right_id

        if "|" in expr and "!" in expr:
            parts = [p.strip() for p in expr.split("|")]
            if (
                len(parts) == 2
                and parts[0].startswith("!")
                and parts[1].startswith("!")
            ):
                left_id = self._resolve_name(parts[0][1:], name_to_id)
                right_id = self._resolve_name(parts[1][1:], name_to_id)
                return "excludes", left_id, right_id

        return None

    def _extract_uvl_relations(
        self, constraints: List[str], parsed: Dict[str, ParsedNode]
    ) -> set[tuple[str, str, str]]:
        name_to_id = {
            self._normalize_name(name): self._normalize_name(name)
            for name in parsed.keys()
        }
        relations = set()
        for raw in constraints:
            parsed_constraint = self._parse_constraint(raw, name_to_id)
            if parsed_constraint is None:
                continue
            ctype, left_id, right_id = parsed_constraint
            rel_type = "requires" if ctype == "requires" else "excludes"
            relations.add((left_id, right_id, rel_type))
        return relations

    def _extract_uvl_constraints(
        self, constraints: List[str], parsed: Dict[str, ParsedNode]
    ) -> set[str]:
        name_to_id = {
            self._normalize_name(name): self._normalize_name(name)
            for name in parsed.keys()
        }
        normalized = set()
        for raw in constraints:
            if self._parse_constraint(raw, name_to_id) is None:
                normalized.add(raw.strip())
        return normalized

    def _resolve_name(self, token: str, name_to_id: Dict[str, str]) -> str:
        name = token.strip().replace("_", " ").strip()
        normalized = self._normalize_name(name)
        return name_to_id.get(normalized, name)

    def _normalize_name(self, name: str) -> str:
        return name.strip().lower()
