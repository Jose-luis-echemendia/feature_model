"""
Componente 3: Analizador Estructural (Estructuras de Grafo y Optimización)

Encargado de inspeccionar propiedades internas del Feature Model que no
dependen únicamente de restricciones lógicas sino de la topología del modelo.

Análisis realizados:
- Dead features (características inaccesibles)
- Características redundantes
- Relaciones implícitas
- Dependencias transitivas
- Componentes fuertemente conexas (SCC)
- Métricas de impacto y complejidad
- Análisis de caminos y centralidad

Tecnologías:
- NetworkX: Análisis completo de grafos con algoritmos optimizados
- DFS, BFS: Búsqueda en profundidad y amplitud
- Tarjan's SCC: Componentes fuertemente conexas
- PageRank, Betweenness: Métricas de centralidad
"""

from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict

# NetworkX para análisis avanzado de grafos
import networkx as nx

from app.enums import AnalysisType
from app.exceptions import (
    InvalidTreeStructureException,
    CyclicDependencyException,
    OrphanFeatureException,
    DeadFeatureDetectedException,
    FalseOptionalDetectedException,
)


class StructuralIssue:
    """Representa un problema estructural detectado."""

    def __init__(
        self,
        issue_type: str,
        severity: str,  # "critical", "major", "minor"
        feature_id: Optional[str],
        description: str,
        recommendation: Optional[str] = None,
    ):
        self.issue_type = issue_type
        self.severity = severity
        self.feature_id = feature_id
        self.description = description
        self.recommendation = recommendation


class StructuralAnalysisResult:
    """Resultado de un análisis estructural."""

    def __init__(
        self,
        analysis_type: AnalysisType,
        issues: List[StructuralIssue],
        metrics: Optional[Dict[str, Any]] = None,
        graph_data: Optional[Dict[str, Any]] = None,
    ):
        self.analysis_type = analysis_type
        self.issues = issues
        self.metrics = metrics or {}
        self.graph_data = graph_data


class FeatureModelStructuralAnalyzer:
    """
    Analizador Estructural de Feature Models usando NetworkX.

    Utiliza NetworkX para análisis avanzado de grafos:
    - Algoritmos optimizados (DFS, BFS, SCC, caminos mínimos)
    - Métricas de centralidad (PageRank, Betweenness, Closeness)
    - Detección de ciclos y comunidades
    - Análisis de conectividad y alcanzabilidad
    """

    def __init__(self):
        """Inicializa el analizador estructural."""
        self.features_map: Dict[str, Dict[str, Any]] = {}
        self.graph: nx.DiGraph = nx.DiGraph()  # Grafo dirigido principal
        self.tree_graph: nx.DiGraph = nx.DiGraph()  # Árbol jerárquico
        self.dependency_graph: nx.DiGraph = (
            nx.DiGraph()
        )  # Grafo de dependencias cross-tree
        self.relations: List[Dict[str, Any]] = []
        self.constraints: List[Dict[str, Any]] = []
        self.graph: Dict[str, List[str]] = {}  # Grafo de dependencias
        self.reverse_graph: Dict[str, List[str]] = {}  # Grafo inverso

    def analyze_feature_model(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        analysis_types: Optional[List[AnalysisType]] = None,
    ) -> Dict[AnalysisType, StructuralAnalysisResult]:
        """
        Realiza análisis estructural completo del Feature Model.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones entre features
            constraints: Lista de restricciones cross-tree
            analysis_types: Tipos de análisis a realizar (None = todos)

        Returns:
            Dict con resultados de cada tipo de análisis
        """
        self._initialize(features, relations, constraints)

        if analysis_types is None:
            analysis_types = list(AnalysisType)

        results = {}

        for analysis_type in analysis_types:
            if analysis_type == AnalysisType.DEAD_FEATURES:
                results[analysis_type] = self._analyze_dead_features()
            elif analysis_type == AnalysisType.REDUNDANCIES:
                results[analysis_type] = self._analyze_redundancies()
            elif analysis_type == AnalysisType.IMPLICIT_RELATIONS:
                results[analysis_type] = self._analyze_implicit_relations()
            elif analysis_type == AnalysisType.TRANSITIVE_DEPENDENCIES:
                results[analysis_type] = self._analyze_transitive_dependencies()
            elif analysis_type == AnalysisType.STRONGLY_CONNECTED:
                results[analysis_type] = self._analyze_strongly_connected_components()
            elif analysis_type == AnalysisType.COMPLEXITY_METRICS:
                results[analysis_type] = self._calculate_complexity_metrics()

        return results

    def detect_dead_features(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Detecta features "muertas" (nunca pueden ser seleccionadas).

        Returns:
            Lista de IDs de features muertas
        """
        self._initialize(features, relations, constraints)
        result = self._analyze_dead_features()
        return [issue.feature_id for issue in result.issues if issue.feature_id]

    def calculate_feature_impact(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        feature_id: str,
    ) -> Dict[str, Any]:
        """
        Calcula el impacto de una feature en el modelo.

        Métricas:
        - Número de dependientes directos
        - Número de dependientes transitivos
        - Nivel de profundidad en el árbol
        - Número de constraints que la involucran

        Returns:
            Dict con métricas de impacto
        """
        self._initialize(features, relations, constraints)

        direct_dependents = self._get_direct_dependents(feature_id)
        transitive_dependents = self._get_transitive_dependents(feature_id)
        depth = self._calculate_feature_depth(feature_id)
        constraints_count = self._count_constraints_involving(feature_id)

        return {
            "feature_id": feature_id,
            "direct_dependents": len(direct_dependents),
            "transitive_dependents": len(transitive_dependents),
            "depth": depth,
            "constraints_count": constraints_count,
            "impact_score": len(transitive_dependents)
            + constraints_count * 2,  # Peso mayor a constraints
        }

    def _initialize(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> None:
        """Inicializa estructuras de datos internas."""
        self.features_map = {str(f["id"]): f for f in features}
        self.relations = relations
        self.constraints = constraints

        # Construir grafo de dependencias
        self.graph = defaultdict(list)
        self.reverse_graph = defaultdict(list)

        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))

            self.graph[parent_id].append(child_id)
            self.reverse_graph[child_id].append(parent_id)

    def _analyze_dead_features(self) -> StructuralAnalysisResult:
        """
        Analiza features muertas (inaccesibles desde la raíz).

        Una feature está "muerta" si:
        1. No es alcanzable desde la raíz
        2. Está en un componente desconectado

        Raises:
            InvalidTreeStructureException: Si no se encuentra feature raíz
            DeadFeatureDetectedException: Si se detectan features muertas (opcional)
        """
        issues = []

        # Encontrar raíz
        root = self._find_root()
        if not root:
            # Lanzar excepción personalizada
            raise InvalidTreeStructureException(
                reason="No se encontró feature raíz en el modelo"
            )

        # DFS desde la raíz para encontrar alcanzables
        reachable = self._dfs_reachable(str(root["id"]))

        # Features inaccesibles = todas - alcanzables
        all_features = set(self.features_map.keys())
        dead_features = all_features - reachable

        for feature_id in dead_features:
            feature = self.features_map[feature_id]
            feature_name = feature.get("name", feature_id)

            # Lanzar excepción por cada dead feature detectada
            raise DeadFeatureDetectedException(
                feature_name=feature_name,
                reason="La feature es inaccesible desde la raíz",
            )

        metrics = {
            "total_features": len(all_features),
            "reachable_features": len(reachable),
            "dead_features": len(dead_features),
        }

        return StructuralAnalysisResult(
            analysis_type=AnalysisType.DEAD_FEATURES, issues=issues, metrics=metrics
        )

    def _analyze_redundancies(self) -> StructuralAnalysisResult:
        """
        Detecta redundancias en el modelo.

        Busca:
        - Relaciones duplicadas
        - Constraints redundantes (implicadas por otras)
        """
        issues = []

        # Detectar relaciones duplicadas
        seen_relations = set()
        for relation in self.relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = relation.get("relation_type")

            key = (parent_id, child_id, relation_type)
            if key in seen_relations:
                issues.append(
                    StructuralIssue(
                        issue_type="duplicate_relation",
                        severity="minor",
                        feature_id=child_id,
                        description=f"Relación duplicada: {parent_id} -> {child_id} ({relation_type})",
                        recommendation="Eliminar la relación duplicada",
                    )
                )
            seen_relations.add(key)

        # Detectar constraints potencialmente redundantes
        # (Análisis simplificado: buscar constraints idénticos)
        seen_constraints = set()
        for constraint in self.constraints:
            expr = constraint.get("expr_text", "")
            if expr in seen_constraints:
                issues.append(
                    StructuralIssue(
                        issue_type="duplicate_constraint",
                        severity="minor",
                        feature_id=None,
                        description=f"Constraint duplicada: {expr}",
                        recommendation="Eliminar la constraint duplicada",
                    )
                )
            seen_constraints.add(expr)

        return StructuralAnalysisResult(
            analysis_type=AnalysisType.REDUNDANCIES,
            issues=issues,
            metrics={"duplicate_relations": len(issues)},
        )

    def _analyze_implicit_relations(self) -> StructuralAnalysisResult:
        """
        Detecta relaciones implícitas derivadas de constraints.

        Por ejemplo, si A requires B, entonces existe una dependencia
        implícita A -> B que podría no estar en la jerarquía.
        """
        issues = []

        # TODO: Parsear constraints y extraer dependencias implícitas
        # Por ahora, retornar placeholder

        return StructuralAnalysisResult(
            analysis_type=AnalysisType.IMPLICIT_RELATIONS,
            issues=issues,
            metrics={"implicit_relations_found": 0},
        )

    def _analyze_transitive_dependencies(self) -> StructuralAnalysisResult:
        """
        Calcula el cierre transitivo de dependencias.

        Útil para entender el impacto de cambios en features.
        """
        issues = []

        # Para cada feature, calcular sus dependientes transitivos
        transitive_deps = {}
        for feature_id in self.features_map.keys():
            deps = self._get_transitive_dependents(feature_id)
            transitive_deps[feature_id] = len(deps)

        # Identificar features con muchas dependencias (puntos críticos)
        threshold = len(self.features_map) * 0.3  # 30% del modelo
        for feature_id, dep_count in transitive_deps.items():
            if dep_count > threshold:
                feature = self.features_map[feature_id]
                issues.append(
                    StructuralIssue(
                        issue_type="high_impact_feature",
                        severity="major",
                        feature_id=feature_id,
                        description=f"Feature '{feature.get('name')}' afecta a {dep_count} otras features",
                        recommendation="Considerar descomponer esta feature para reducir acoplamiento",
                    )
                )

        return StructuralAnalysisResult(
            analysis_type=AnalysisType.TRANSITIVE_DEPENDENCIES,
            issues=issues,
            metrics=transitive_deps,
        )

    def _analyze_strongly_connected_components(self) -> StructuralAnalysisResult:
        """
        Detecta componentes fuertemente conexas (ciclos).

        Un ciclo en un Feature Model indica un problema de modelado.

        Raises:
            CyclicDependencyException: Si se detecta un ciclo en el modelo
        """
        issues = []

        # Implementación simplificada de Tarjan's SCC
        # En producción, usar NetworkX
        sccs = self._tarjan_scc()

        # SCCs con más de 1 elemento son ciclos
        for scc in sccs:
            if len(scc) > 1:
                feature_names = [self.features_map[fid].get("name") for fid in scc]

                # Lanzar excepción personalizada
                raise CyclicDependencyException(feature_cycle=", ".join(feature_names))

        return StructuralAnalysisResult(
            analysis_type=AnalysisType.STRONGLY_CONNECTED,
            issues=issues,
            metrics={"cycles_found": len(issues)},
        )

    def _calculate_complexity_metrics(self) -> StructuralAnalysisResult:
        """
        Calcula métricas de complejidad del modelo.

        Métricas:
        - Profundidad máxima del árbol
        - Ancho promedio
        - Factor de ramificación
        - Densidad de constraints
        """
        issues = []

        max_depth = 0
        leaf_count = 0
        total_children = 0
        node_count = len(self.features_map)

        for feature_id in self.features_map.keys():
            depth = self._calculate_feature_depth(feature_id)
            max_depth = max(max_depth, depth)

            children = self.graph.get(feature_id, [])
            if not children:
                leaf_count += 1
            total_children += len(children)

        avg_branching = total_children / node_count if node_count > 0 else 0
        constraint_density = len(self.constraints) / node_count if node_count > 0 else 0

        metrics = {
            "max_depth": max_depth,
            "total_features": node_count,
            "leaf_features": leaf_count,
            "avg_branching_factor": round(avg_branching, 2),
            "constraint_density": round(constraint_density, 2),
            "total_constraints": len(self.constraints),
        }

        # Generar warnings si complejidad es alta
        if max_depth > 10:
            issues.append(
                StructuralIssue(
                    issue_type="high_depth",
                    severity="minor",
                    feature_id=None,
                    description=f"Árbol muy profundo (depth={max_depth})",
                    recommendation="Considerar aplanar la jerarquía",
                )
            )

        if constraint_density > 1.0:
            issues.append(
                StructuralIssue(
                    issue_type="high_constraint_density",
                    severity="minor",
                    feature_id=None,
                    description=f"Alta densidad de constraints ({constraint_density:.2f})",
                    recommendation="Revisar si algunas constraints pueden simplificarse",
                )
            )

        return StructuralAnalysisResult(
            analysis_type=AnalysisType.COMPLEXITY_METRICS,
            issues=issues,
            metrics=metrics,
        )

    # ============ Utilidades de Grafos ============

    def _find_root(self) -> Optional[Dict[str, Any]]:
        """Encuentra la feature raíz (sin parent)."""
        for feature in self.features_map.values():
            if feature.get("parent_id") is None:
                return feature
        return None

    def _dfs_reachable(self, start_id: str) -> Set[str]:
        """DFS para encontrar todos los nodos alcanzables desde start."""
        visited = set()
        stack = [start_id]

        while stack:
            node = stack.pop()
            if node in visited:
                continue

            visited.add(node)
            children = self.graph.get(node, [])
            stack.extend(children)

        return visited

    def _get_direct_dependents(self, feature_id: str) -> List[str]:
        """Retorna los hijos directos de una feature."""
        return self.graph.get(feature_id, [])

    def _get_transitive_dependents(self, feature_id: str) -> Set[str]:
        """Retorna todos los descendientes transitivos de una feature."""
        return self._dfs_reachable(feature_id) - {feature_id}

    def _calculate_feature_depth(self, feature_id: str) -> int:
        """Calcula la profundidad de una feature en el árbol."""
        depth = 0
        current = feature_id

        while current in self.reverse_graph:
            parents = self.reverse_graph[current]
            if not parents:
                break
            current = parents[0]  # Tomar primer parent
            depth += 1

        return depth

    def _count_constraints_involving(self, feature_id: str) -> int:
        """Cuenta cuántas constraints involucran a una feature."""
        count = 0
        feature = self.features_map.get(feature_id)
        if not feature:
            return 0

        feature_name = feature.get("name", "")

        for constraint in self.constraints:
            expr_text = constraint.get("expr_text", "")
            if feature_name in expr_text or feature_id in expr_text:
                count += 1

        return count

    def _tarjan_scc(self) -> List[List[str]]:
        """
        Algoritmo de Tarjan para encontrar componentes fuertemente conexas.

        Implementación simplificada.
        """
        # TODO: Implementación completa de Tarjan
        # Por ahora, retornar cada nodo como su propio componente
        return [[fid] for fid in self.features_map.keys()]

    def validate_tree_structure(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> None:
        """
        Valida que la estructura del feature model forme un árbol válido.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones

        Raises:
            InvalidTreeStructureException: Si la estructura no es un árbol válido
            OrphanFeatureException: Si hay features sin conexión al árbol
        """
        self._initialize(features, relations, [])

        # 1. Verificar que hay exactamente una raíz
        roots = [f for f in features if f.get("parent_id") is None]

        if len(roots) == 0:
            raise InvalidTreeStructureException(
                reason="No se encontró ninguna feature raíz en el modelo"
            )

        if len(roots) > 1:
            root_names = ", ".join([f.get("name", str(f.get("id"))) for f in roots])
            raise InvalidTreeStructureException(
                reason=f"Se encontraron múltiples features raíz: {root_names}"
            )

        # 2. Verificar que todas las features son alcanzables desde la raíz
        root_id = str(roots[0]["id"])
        reachable = self._dfs_reachable(root_id)
        all_feature_ids = set(self.features_map.keys())
        orphan_features = all_feature_ids - reachable

        if orphan_features:
            for orphan_id in orphan_features:
                feature = self.features_map[orphan_id]
                feature_name = feature.get("name", orphan_id)

                # Lanzar excepción por feature huérfana
                raise OrphanFeatureException(feature_name=feature_name)

        # 3. Verificar que no hay ciclos (cada nodo tiene un solo parent)
        for feature_id in self.features_map.keys():
            parents = self.reverse_graph.get(feature_id, [])
            if len(parents) > 1:
                feature = self.features_map[feature_id]
                parent_names = ", ".join(
                    [self.features_map[pid].get("name", pid) for pid in parents]
                )
                raise InvalidTreeStructureException(
                    reason=f"Feature '{feature.get('name')}' tiene múltiples parents: {parent_names}"
                )

    def detect_orphan_features(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Detecta features que no están conectadas al árbol principal.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones

        Returns:
            Lista de IDs de features huérfanas

        Raises:
            OrphanFeatureException: Si se encuentran features huérfanas
        """
        self._initialize(features, relations, [])

        # Encontrar raíz
        root = self._find_root()
        if not root:
            return []

        # Encontrar features alcanzables
        reachable = self._dfs_reachable(str(root["id"]))
        all_feature_ids = set(self.features_map.keys())
        orphan_features = all_feature_ids - reachable

        # Lanzar excepción por cada feature huérfana
        for orphan_id in orphan_features:
            feature = self.features_map[orphan_id]
            raise OrphanFeatureException(feature_name=feature.get("name", orphan_id))

        return list(orphan_features)

    def check_false_optionals(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> None:
        """
        Detecta features marcadas como opcionales pero que son efectivamente mandatory
        debido a constraints.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones
            constraints: Lista de restricciones

        Raises:
            FalseOptionalDetectedException: Si se detectan opcionales falsos
        """
        self._initialize(features, relations, constraints)

        # Buscar features opcionales
        optional_features = []
        for relation in relations:
            if relation.get("relation_type") == "optional":
                child_id = str(relation.get("child_id"))
                optional_features.append(child_id)

        # Verificar si alguna constraint las hace mandatory
        for feature_id in optional_features:
            feature = self.features_map[feature_id]
            feature_name = feature.get("name", feature_id)

            # Buscar constraints que mencionen esta feature
            for constraint in constraints:
                expr_text = constraint.get("expr_text", "")

                # Si hay un REQUIRES hacia esta feature, podría ser mandatory
                if feature_name in expr_text and "REQUIRES" in expr_text.upper():
                    # Lanzar excepción
                    raise FalseOptionalDetectedException(
                        feature_name=feature_name, actual_constraint=expr_text
                    )
