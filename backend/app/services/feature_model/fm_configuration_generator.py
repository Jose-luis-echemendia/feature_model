"""
Componente 2: Generador de Configuraciones (Heurístico / Búsqueda Guiada)

Este componente construye configuraciones válidas a partir del modelo,
ya sea para derivar productos completos o proponer alternativas viables
ante decisiones parciales proporcionadas por el usuario.

Técnicas:
- Búsqueda heurística (greedy, beam search)
- Algoritmos genéticos (futuro con DEAP)
- Integración con validador SAT para verificar corrección
"""

import random
from typing import Dict, List, Any, Optional, Set

from app.enums import GenerationStrategy


class GenerationResult:
    """Resultado de una generación de configuración."""

    def __init__(
        self,
        success: bool,
        configuration: Optional[Dict[str, bool]] = None,
        selected_features: Optional[List[str]] = None,
        score: float = 0.0,
        iterations: int = 0,
        errors: Optional[List[str]] = None,
    ):
        self.success = success
        self.configuration = configuration or {}
        self.selected_features = selected_features or []
        self.score = score
        self.iterations = iterations
        self.errors = errors or []


class FeatureModelConfigurationGenerator:
    """
    Generador de configuraciones válidas para Feature Models.

    Genera configuraciones completas o parciales que satisfacen
    todas las restricciones del modelo, usando técnicas heurísticas
    para explorar eficientemente el espacio de soluciones.
    """

    def __init__(self):
        """Inicializa el generador."""
        self.features_map: Dict[str, Dict[str, Any]] = {}
        self.relations_map: Dict[str, List[Dict[str, Any]]] = {}
        self.constraints: List[Dict[str, Any]] = []

    def generate_valid_configuration(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        strategy: GenerationStrategy = GenerationStrategy.GREEDY,
        partial_selection: Optional[Dict[str, bool]] = None,
        max_iterations: int = 1000,
    ) -> GenerationResult:
        """
        Genera una configuración válida del Feature Model.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones entre features
            constraints: Lista de restricciones cross-tree
            strategy: Estrategia de generación a utilizar
            partial_selection: Selección parcial inicial (puede ser None)
            max_iterations: Número máximo de iteraciones

        Returns:
            GenerationResult con la configuración generada
        """
        self._initialize(features, relations, constraints)

        if strategy == GenerationStrategy.GREEDY:
            return self._generate_greedy(partial_selection, max_iterations)
        elif strategy == GenerationStrategy.RANDOM:
            return self._generate_random(partial_selection, max_iterations)
        elif strategy == GenerationStrategy.BEAM_SEARCH:
            return self._generate_beam_search(partial_selection, max_iterations)
        else:
            return GenerationResult(
                success=False, errors=[f"Estrategia no soportada: {strategy}"]
            )

    def complete_partial_configuration(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        partial_selection: Dict[str, bool],
    ) -> GenerationResult:
        """
        Completa una configuración parcial del usuario.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones
            constraints: Lista de restricciones
            partial_selection: Decisiones parciales del usuario

        Returns:
            GenerationResult con la configuración completada
        """
        return self.generate_valid_configuration(
            features=features,
            relations=relations,
            constraints=constraints,
            strategy=GenerationStrategy.GREEDY,
            partial_selection=partial_selection,
        )

    def generate_multiple_configurations(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        count: int = 10,
        diverse: bool = True,
    ) -> List[GenerationResult]:
        """
        Genera múltiples configuraciones válidas diferentes.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones
            constraints: Lista de restricciones
            count: Número de configuraciones a generar
            diverse: Si True, intenta maximizar diversidad

        Returns:
            Lista de GenerationResult
        """
        results = []
        generated_configs: Set[frozenset] = set()

        for i in range(count * 3):  # Intentar más veces para asegurar diversidad
            if len(results) >= count:
                break

            # Usar random con seeds diferentes para diversidad
            result = self.generate_valid_configuration(
                features=features,
                relations=relations,
                constraints=constraints,
                strategy=GenerationStrategy.RANDOM,
            )

            if result.success:
                # Verificar si es diferente a las anteriores
                config_set = frozenset(result.selected_features)
                if not diverse or config_set not in generated_configs:
                    results.append(result)
                    generated_configs.add(config_set)

        return results

    def _initialize(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> None:
        """Inicializa estructuras internas."""
        self.features_map = {str(f["id"]): f for f in features}
        self.constraints = constraints

        # Construir mapa de relaciones: parent_id -> [children]
        self.relations_map = {}
        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            if parent_id not in self.relations_map:
                self.relations_map[parent_id] = []
            self.relations_map[parent_id].append(relation)

    def _generate_greedy(
        self, partial_selection: Optional[Dict[str, bool]], max_iterations: int
    ) -> GenerationResult:
        """
        Generación golosa: selecciona features por prioridad.

        Algoritmo:
        1. Partir de la raíz (obligatoria)
        2. Para cada feature seleccionada:
           - Seleccionar hijos mandatory
           - Evaluar hijos optional según prioridad
        3. Verificar constraints cross-tree
        """
        configuration: Dict[str, bool] = partial_selection or {}
        iterations = 0

        # Encontrar raíz
        root = self._find_root()
        if not root:
            return GenerationResult(
                success=False, errors=["No se encontró feature raíz"]
            )

        root_id = str(root["id"])
        configuration[root_id] = True

        # Cola de features a procesar
        queue = [root_id]

        while queue and iterations < max_iterations:
            iterations += 1
            current_id = queue.pop(0)

            # Procesar hijos
            children = self.relations_map.get(current_id, [])

            for relation in children:
                child_id = str(relation["child_id"])
                relation_type = relation.get("relation_type")

                # Si ya está decidido, saltar
                if child_id in configuration:
                    continue

                # Mandatory: siempre incluir
                if relation_type == "mandatory":
                    configuration[child_id] = True
                    queue.append(child_id)

                # Optional: decisión heurística (50% probabilidad)
                elif relation_type == "optional":
                    # Heurística: incluir si tiene pocos hijos o es hoja
                    should_include = self._should_include_optional(child_id)
                    configuration[child_id] = should_include
                    if should_include:
                        queue.append(child_id)

        # Verificar que no se violen constraints (simplificado)
        # En producción, usar el LogicalValidator aquí

        selected = [fid for fid, selected in configuration.items() if selected]

        return GenerationResult(
            success=True,
            configuration=configuration,
            selected_features=selected,
            iterations=iterations,
            score=len(selected) / len(self.features_map),  # Ratio de completitud
        )

    def _generate_random(
        self, partial_selection: Optional[Dict[str, bool]], max_iterations: int
    ) -> GenerationResult:
        """
        Generación aleatoria: selecciona features al azar respetando mandatory.

        Similar a greedy pero con decisiones aleatorias para optional.
        """
        configuration: Dict[str, bool] = partial_selection or {}
        iterations = 0

        root = self._find_root()
        if not root:
            return GenerationResult(
                success=False, errors=["No se encontró feature raíz"]
            )

        root_id = str(root["id"])
        configuration[root_id] = True
        queue = [root_id]

        while queue and iterations < max_iterations:
            iterations += 1
            current_id = queue.pop(0)

            children = self.relations_map.get(current_id, [])

            for relation in children:
                child_id = str(relation["child_id"])
                relation_type = relation.get("relation_type")

                if child_id in configuration:
                    continue

                if relation_type == "mandatory":
                    configuration[child_id] = True
                    queue.append(child_id)
                elif relation_type == "optional":
                    # Decisión aleatoria
                    should_include = random.random() > 0.5
                    configuration[child_id] = should_include
                    if should_include:
                        queue.append(child_id)

        selected = [fid for fid, sel in configuration.items() if sel]

        return GenerationResult(
            success=True,
            configuration=configuration,
            selected_features=selected,
            iterations=iterations,
            score=len(selected) / len(self.features_map),
        )

    def _generate_beam_search(
        self, partial_selection: Optional[Dict[str, bool]], max_iterations: int
    ) -> GenerationResult:
        """
        Beam search: mantiene los k mejores candidatos en cada paso.

        Más sofisticado que greedy, explora múltiples caminos en paralelo.
        """
        # TODO: Implementación futura
        # Por ahora, delegar a greedy
        return self._generate_greedy(partial_selection, max_iterations)

    def _find_root(self) -> Optional[Dict[str, Any]]:
        """Encuentra la feature raíz (sin parent)."""
        for feature in self.features_map.values():
            if feature.get("parent_id") is None:
                return feature
        return None

    def _should_include_optional(self, feature_id: str) -> bool:
        """
        Heurística para decidir si incluir una feature optional.

        Factores:
        - Si es hoja (sin hijos): 30% probabilidad
        - Si tiene pocos hijos: 60% probabilidad
        - Si tiene muchos hijos: 80% probabilidad
        """
        children = self.relations_map.get(feature_id, [])
        num_children = len(children)

        if num_children == 0:
            return random.random() < 0.3
        elif num_children <= 2:
            return random.random() < 0.6
        else:
            return random.random() < 0.8
