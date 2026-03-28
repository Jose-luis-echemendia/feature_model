"""
Componente 2: Generador de Configuraciones (Heurístico / Búsqueda Guiada)

Este componente construye configuraciones válidas a partir del modelo,
ya sea para derivar productos completos o proponer alternativas viables
ante decisiones parciales proporcionadas por el usuario.

Técnicas implementadas:
- Búsqueda heurística: GREEDY (golosa), RANDOM (aleatoria)
- Beam Search: Búsqueda en haz (explorando múltiples caminos)
- Algoritmos genéticos: DEAP para evolución de configuraciones
- Integración formal: Verificación con SAT solvers

Estrategias disponibles:
1. GREEDY: Rápida, determinista, prioridad por mandatory
2. RANDOM: Estocástica, diversidad de soluciones
3. BEAM_SEARCH: Balance entre exhaustividad y eficiencia
4. GENETIC: Optimización multi-objetivo con algoritmos evolutivos
"""

import random
from typing import Dict, List, Any, Optional, Set, Callable

from app.enums import GenerationStrategy
from app.services.feature_model.fm_logical_validator import (
    FeatureModelLogicalValidator,
)
from app.exceptions import InvalidConfigurationException

# DEAP para algoritmos genéticos
try:
    from deap import base, creator, tools, algorithms
    import numpy as np

    DEAP_AVAILABLE = True
except ImportError:
    DEAP_AVAILABLE = False


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
    Generador de configuraciones válidas para Feature Models - 3 Estrategias.

    Genera configuraciones completas o parciales que satisfacen
    todas las restricciones del modelo.

    Estrategias disponibles:
    1. GREEDY: Selección golosa (rápida, determinista)
    2. RANDOM: Selección aleatoria (diversidad)
    3. BEAM_SEARCH: Búsqueda en haz (balance exploración/explotación)
    4. GENETIC: Algoritmos genéticos con DEAP (optimización multi-objetivo)
    """

    def __init__(self):
        """Inicializa el generador."""
        self.features_map: Dict[str, Dict[str, Any]] = {}
        self.relations_map: Dict[str, List[Dict[str, Any]]] = {}
        self.constraints: List[Dict[str, Any]] = []

        # Configuración para algoritmos genéticos (DEAP)
        self.deap_toolbox: tools.Toolbox | None = None
        self.population_size: int = 50
        self.num_generations: int = 100

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
            return self._generate_with_validation(
                self._generate_greedy,
                features,
                relations,
                constraints,
                partial_selection,
                max_iterations,
            )
        elif strategy == GenerationStrategy.RANDOM:
            return self._generate_with_validation(
                self._generate_random,
                features,
                relations,
                constraints,
                partial_selection,
                max_iterations,
            )
        elif strategy == GenerationStrategy.BEAM_SEARCH:
            return self._generate_with_validation(
                self._generate_beam_search,
                features,
                relations,
                constraints,
                partial_selection,
                max_iterations,
            )
        elif strategy == GenerationStrategy.GENETIC:
            if DEAP_AVAILABLE:
                return self._generate_with_validation(
                    self._generate_genetic,
                    features,
                    relations,
                    constraints,
                    partial_selection,
                    max_iterations,
                )
            return self._generate_with_validation(
                self._generate_random,
                features,
                relations,
                constraints,
                partial_selection,
                max_iterations,
            )

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
        beam_width = 5
        feature_ids = list(self.features_map.keys())
        optional_ids = self._get_optional_features()

        # Config inicial
        base_config = partial_selection.copy() if partial_selection else {}
        root = self._find_root()
        if not root:
            return GenerationResult(
                success=False, errors=["No se encontró feature raíz"]
            )
        base_config[str(root["id"])] = True
        self._propagate_mandatory(base_config)

        beam: List[Dict[str, bool]] = [base_config]
        iterations = 0

        for fid in optional_ids:
            iterations += 1
            if iterations > max_iterations:
                break
            new_beam: List[Dict[str, bool]] = []
            for config in beam:
                if fid in config:
                    new_beam.append(config)
                    continue
                for value in (False, True):
                    candidate = config.copy()
                    candidate[fid] = value
                    self._propagate_mandatory(candidate)
                    new_beam.append(candidate)

            # Rankear candidatos
            scored = [(self._score_configuration(c, feature_ids), c) for c in new_beam]
            scored.sort(key=lambda x: x[0], reverse=True)
            beam = [c for _, c in scored[:beam_width]]

        best_config = beam[0] if beam else base_config
        selected = [fid for fid, sel in best_config.items() if sel]

        return GenerationResult(
            success=True,
            configuration=best_config,
            selected_features=selected,
            iterations=iterations,
            score=self._score_configuration(best_config, feature_ids),
        )

    def _generate_genetic(
        self, partial_selection: Optional[Dict[str, bool]], max_iterations: int
    ) -> GenerationResult:
        """
        Generación usando algoritmos genéticos con DEAP.

        Evoluciona una población de configuraciones para encontrar
        soluciones óptimas según múltiples criterios:
        - Maximizar features seleccionadas
        - Minimizar violaciones de restricciones
        - Respetar decisiones parciales del usuario

        Returns:
            GenerationResult con la mejor configuración encontrada
        """
        if not DEAP_AVAILABLE:
            return GenerationResult(
                success=False,
                errors=["DEAP no disponible, instalar con: pip install deap"],
            )

        # 1. Configurar DEAP
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        # 2. Definir representación (lista de booleanos, uno por feature)
        feature_ids = list(self.features_map.keys())
        n_features = len(feature_ids)

        def create_individual():
            """Crear un individuo aleatorio (configuración)."""
            # Si hay selección parcial, respetarla
            if partial_selection:
                individual = [
                    partial_selection.get(fid, random.choice([True, False]))
                    for fid in feature_ids
                ]
            else:
                individual = [random.choice([True, False]) for _ in range(n_features)]
            return creator.Individual(individual)

        toolbox.register("individual", create_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # 3. Función de fitness (cuántas features válidas)
        def evaluate(individual):
            """Evaluar calidad de una configuración."""
            config = {fid: sel for fid, sel in zip(feature_ids, individual)}
            selected = [fid for fid, sel in config.items() if sel]

            # Penalizar configuraciones vacías
            if len(selected) == 0:
                return (0.0,)

            # Validar restricciones
            if not self._is_valid_configuration(selected):
                return (0.0,)

            # Score: número de features / total
            score = len(selected) / n_features
            return (score,)

        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # 4. Ejecutar algoritmo genético
        population = toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(1)  # Mejor individuo

        # Ejecutar evolución
        algorithms.eaSimple(
            population,
            toolbox,
            cxpb=0.7,  # Probabilidad de cruce
            mutpb=0.2,  # Probabilidad de mutación
            ngen=min(self.num_generations, max_iterations // self.population_size),
            halloffame=hof,
            verbose=False,
        )

        # 5. Extraer mejor solución
        best_individual = hof[0]
        configuration = {fid: sel for fid, sel in zip(feature_ids, best_individual)}
        selected = [fid for fid, sel in configuration.items() if sel]

        return GenerationResult(
            success=True,
            configuration=configuration,
            selected_features=selected,
            iterations=self.num_generations,
            score=best_individual.fitness.values[0],
        )

    def _generate_with_validation(
        self,
        generator: Callable[[Optional[Dict[str, bool]], int], GenerationResult],
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        partial_selection: Optional[Dict[str, bool]],
        max_iterations: int,
    ) -> GenerationResult:
        """Envuelve estrategias con validación SAT/SMT."""
        self._validator = FeatureModelLogicalValidator()
        attempts = min(20, max_iterations)

        for _ in range(attempts):
            result = generator(partial_selection, max_iterations)
            if not result.success:
                continue
            if self._is_valid_configuration(
                result.selected_features, features, relations, constraints
            ):
                return result

        return GenerationResult(
            success=False,
            errors=["No se encontró configuración válida bajo las restricciones"],
        )

    def _is_valid_configuration(
        self,
        selected_features: List[str],
        features: Optional[List[Dict[str, Any]]] = None,
        relations: Optional[List[Dict[str, Any]]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Valida una configuración con el LogicalValidator."""
        features = features or list(self.features_map.values())
        relations = relations or [
            r for rels in self.relations_map.values() for r in rels
        ]
        constraints = constraints or self.constraints

        try:
            validator = FeatureModelLogicalValidator()
            validator.validate_configuration(
                features, relations, constraints, selected_features
            )
            return True
        except InvalidConfigurationException:
            return False
        except Exception:
            return False

    def _get_optional_features(self) -> List[str]:
        """Obtiene ids de features optional basadas en relaciones."""
        optional_ids = []
        for rels in self.relations_map.values():
            for relation in rels:
                if relation.get("relation_type") == "optional":
                    optional_ids.append(str(relation.get("child_id")))
        return optional_ids

    def _propagate_mandatory(self, configuration: Dict[str, bool]) -> None:
        """Propaga selección de mandatory desde parents seleccionados."""
        changed = True
        while changed:
            changed = False
            for rels in self.relations_map.values():
                for relation in rels:
                    if relation.get("relation_type") != "mandatory":
                        continue
                    parent_id = str(relation.get("parent_id"))
                    child_id = str(relation.get("child_id"))
                    if configuration.get(parent_id) and not configuration.get(child_id):
                        configuration[child_id] = True
                        changed = True

    def _score_configuration(
        self, configuration: Dict[str, bool], feature_ids: List[str]
    ) -> float:
        """Score heurístico simple basado en completitud."""
        selected = [fid for fid, sel in configuration.items() if sel]
        if not feature_ids:
            return 0.0
        return len(selected) / len(feature_ids)

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
