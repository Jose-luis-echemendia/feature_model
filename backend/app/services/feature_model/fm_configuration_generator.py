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
from itertools import combinations
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

# OR-Tools CP-SAT
try:
    from ortools.sat.python import cp_model

    CP_SAT_AVAILABLE = True
except ImportError:
    CP_SAT_AVAILABLE = False


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
        self._model_signature: Optional[tuple] = None

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
        elif strategy == GenerationStrategy.SAT_ENUM:
            return self._generate_sat_enumeration(
                features,
                relations,
                constraints,
                partial_selection,
            )
        elif strategy == GenerationStrategy.PAIRWISE:
            results = self._generate_pairwise_configurations(
                features=features,
                relations=relations,
                constraints=constraints,
                count=1,
                partial_selection=partial_selection,
            )
            if results:
                return results[0]
            return GenerationResult(
                success=False,
                errors=["No se pudo generar configuración pairwise"],
            )
        elif strategy == GenerationStrategy.UNIFORM:
            results = self._generate_uniform_sample(
                features=features,
                relations=relations,
                constraints=constraints,
                count=1,
                partial_selection=partial_selection,
            )
            if results:
                return results[0]
            return GenerationResult(
                success=False,
                errors=["No se pudo generar configuración uniforme"],
            )
        elif strategy == GenerationStrategy.STRATIFIED:
            results = self._generate_stratified_sample(
                features=features,
                relations=relations,
                constraints=constraints,
                count=1,
                partial_selection=partial_selection,
            )
            if results:
                return results[0]
            return GenerationResult(
                success=False,
                errors=["No se pudo generar configuración estratificada"],
            )
        elif strategy == GenerationStrategy.CP_SAT:
            return self._generate_cp_sat(
                features=features,
                relations=relations,
                constraints=constraints,
                partial_selection=partial_selection,
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
        strategy: GenerationStrategy = GenerationStrategy.RANDOM,
        partial_selection: Optional[Dict[str, bool]] = None,
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

        if strategy == GenerationStrategy.SAT_ENUM:
            validator = FeatureModelLogicalValidator()
            try:
                solutions = validator.enumerate_configurations(
                    features=features,
                    relations=relations,
                    constraints=constraints,
                    max_solutions=count,
                    partial_selection=partial_selection,
                )
            except Exception as exc:
                return [
                    GenerationResult(
                        success=False,
                        errors=[str(exc)],
                    )
                ]

            for selected in solutions:
                configuration = {
                    str(feature.get("id")): str(feature.get("id")) in selected
                    for feature in features
                }
                results.append(
                    GenerationResult(
                        success=True,
                        configuration=configuration,
                        selected_features=selected,
                        score=self._score_configuration(
                            configuration, list(configuration.keys())
                        ),
                        iterations=0,
                    )
                )

            return results

        if strategy == GenerationStrategy.PAIRWISE:
            return self._generate_pairwise_configurations(
                features=features,
                relations=relations,
                constraints=constraints,
                count=count,
                partial_selection=partial_selection,
            )

        if strategy == GenerationStrategy.UNIFORM:
            return self._generate_uniform_sample(
                features=features,
                relations=relations,
                constraints=constraints,
                count=count,
                partial_selection=partial_selection,
            )

        if strategy == GenerationStrategy.STRATIFIED:
            return self._generate_stratified_sample(
                features=features,
                relations=relations,
                constraints=constraints,
                count=count,
                partial_selection=partial_selection,
            )

        if strategy == GenerationStrategy.CP_SAT:
            return self._generate_cp_sat_multiple(
                features=features,
                relations=relations,
                constraints=constraints,
                count=count,
                partial_selection=partial_selection,
            )

        for i in range(count * 3):  # Intentar más veces para asegurar diversidad
            if len(results) >= count:
                break

            # Usar random con seeds diferentes para diversidad
            result = self.generate_valid_configuration(
                features=features,
                relations=relations,
                constraints=constraints,
                strategy=strategy,
                partial_selection=partial_selection,
            )

            if result.success:
                # Verificar si es diferente a las anteriores
                config_set = frozenset(result.selected_features)
                if not diverse or config_set not in generated_configs:
                    results.append(result)
                    generated_configs.add(config_set)

        return results

    def _generate_pairwise_configurations(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        count: int,
        partial_selection: Optional[Dict[str, bool]] = None,
        max_attempts: int = 2000,
    ) -> List[GenerationResult]:
        """
        Genera configuraciones para cubrir pares (pairwise).
        """
        self._initialize(features, relations, constraints)

        feature_ids = list(self.features_map.keys())
        if len(feature_ids) < 2:
            return [
                GenerationResult(
                    success=True,
                    configuration={fid: True for fid in feature_ids},
                    selected_features=feature_ids,
                    score=1.0 if feature_ids else 0.0,
                    iterations=0,
                )
            ]

        def _pair(a: str, b: str) -> tuple[str, str]:
            return tuple(sorted((a, b)))

        uncovered = {_pair(a, b) for a, b in combinations(feature_ids, 2)}
        results: list[GenerationResult] = []
        seen_configs: set[frozenset[str]] = set()
        attempts = 0

        while uncovered and len(results) < count and attempts < max_attempts:
            attempts += 1
            pair = next(iter(uncovered))
            pair_selection: Dict[str, bool] = {pair[0]: True, pair[1]: True}
            if partial_selection:
                pair_selection.update({str(k): v for k, v in partial_selection.items()})

            result = self.generate_valid_configuration(
                features=features,
                relations=relations,
                constraints=constraints,
                strategy=GenerationStrategy.GREEDY,
                partial_selection=pair_selection,
            )

            if not result.success:
                uncovered.discard(pair)
                continue

            selected_set = frozenset(result.selected_features)
            if selected_set in seen_configs:
                if pair[0] in selected_set and pair[1] in selected_set:
                    uncovered.discard(pair)
                continue

            seen_configs.add(selected_set)
            results.append(result)

            selected_sorted = sorted(result.selected_features)
            for a, b in combinations(selected_sorted, 2):
                uncovered.discard(_pair(a, b))

        return results

    def _generate_uniform_sample(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        count: int,
        partial_selection: Optional[Dict[str, bool]] = None,
        max_pool: int | None = None,
    ) -> List[GenerationResult]:
        """
        Muestreo uniforme aproximado a partir de enumeración SAT.
        """
        validator = FeatureModelLogicalValidator()
        pool_size = max_pool or max(count * 10, 20)
        try:
            solutions = validator.enumerate_configurations(
                features=features,
                relations=relations,
                constraints=constraints,
                max_solutions=pool_size,
                partial_selection=partial_selection,
            )
        except Exception as exc:
            return [GenerationResult(success=False, errors=[str(exc)])]

        if not solutions:
            return [
                GenerationResult(
                    success=False,
                    errors=["No se encontró configuración válida"],
                )
            ]

        sample = (
            random.sample(solutions, k=min(count, len(solutions)))
            if len(solutions) > count
            else solutions
        )

        results: list[GenerationResult] = []
        for selected in sample:
            configuration = {
                str(feature.get("id")): str(feature.get("id")) in selected
                for feature in features
            }
            results.append(
                GenerationResult(
                    success=True,
                    configuration=configuration,
                    selected_features=selected,
                    score=self._score_configuration(
                        configuration, list(configuration.keys())
                    ),
                    iterations=0,
                )
            )

        return results

    def _generate_stratified_sample(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        count: int,
        partial_selection: Optional[Dict[str, bool]] = None,
        bins: int = 3,
    ) -> List[GenerationResult]:
        """
        Muestreo estratificado aproximado por tamaño de selección.
        """
        validator = FeatureModelLogicalValidator()
        pool_size = max(count * 15, 30)
        try:
            solutions = validator.enumerate_configurations(
                features=features,
                relations=relations,
                constraints=constraints,
                max_solutions=pool_size,
                partial_selection=partial_selection,
            )
        except Exception as exc:
            return [GenerationResult(success=False, errors=[str(exc)])]

        if not solutions:
            return [
                GenerationResult(
                    success=False,
                    errors=["No se encontró configuración válida"],
                )
            ]

        sizes = sorted({len(s) for s in solutions})
        if len(sizes) <= bins:
            bin_edges = sizes
        else:
            step = max(len(sizes) // bins, 1)
            bin_edges = sizes[::step][:bins]

        buckets: dict[int, list[list[str]]] = {i: [] for i in range(len(bin_edges))}
        for sol in solutions:
            size = len(sol)
            idx = 0
            for i, edge in enumerate(bin_edges):
                if size >= edge:
                    idx = i
            buckets[idx].append(sol)

        per_bucket = max(count // max(len(buckets), 1), 1)
        selected_solutions: list[list[str]] = []
        for i in buckets:
            bucket = buckets[i]
            if not bucket:
                continue
            pick = min(per_bucket, len(bucket))
            selected_solutions.extend(random.sample(bucket, k=pick))

        while len(selected_solutions) < min(count, len(solutions)):
            selected_solutions.append(random.choice(solutions))

        selected_solutions = selected_solutions[: min(count, len(solutions))]

        results: list[GenerationResult] = []
        for selected in selected_solutions:
            configuration = {
                str(feature.get("id")): str(feature.get("id")) in selected
                for feature in features
            }
            results.append(
                GenerationResult(
                    success=True,
                    configuration=configuration,
                    selected_features=selected,
                    score=self._score_configuration(
                        configuration, list(configuration.keys())
                    ),
                    iterations=0,
                )
            )

        return results

    def _generate_cp_sat(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        partial_selection: Optional[Dict[str, bool]] = None,
    ) -> GenerationResult:
        """
        Genera una configuración usando CP-SAT (OR-Tools).
        """
        if not CP_SAT_AVAILABLE:
            return GenerationResult(
                success=False,
                errors=["OR-Tools no disponible (instalar ortools)"],
            )

        self._initialize(features, relations, constraints)
        model = cp_model.CpModel()

        vars_map = {
            fid: model.NewBoolVar(f"f_{fid}") for fid in self.features_map.keys()
        }

        # Root siempre activa
        for feature in features:
            if feature.get("parent_id") is None:
                fid = str(feature.get("id"))
                if fid in vars_map:
                    model.Add(vars_map[fid] == 1)

        # Jerarquía
        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = relation.get("relation_type")
            if parent_id not in vars_map or child_id not in vars_map:
                continue
            if relation_type == "mandatory":
                model.AddImplication(vars_map[parent_id], vars_map[child_id])
            elif relation_type == "optional":
                model.AddImplication(vars_map[child_id], vars_map[parent_id])

        # Grupos
        groups = self._build_groups_from_relations(relations)
        for group in groups:
            parent_id = group["parent_id"]
            child_ids = group["children"]
            group_type = group["group_type"]
            min_card = group["min_cardinality"]
            max_card = group["max_cardinality"]

            if parent_id not in vars_map:
                continue
            parent_var = vars_map[parent_id]
            child_vars = [vars_map[cid] for cid in child_ids if cid in vars_map]
            if not child_vars:
                continue

            for child_var in child_vars:
                model.AddImplication(child_var, parent_var)

            if group_type == "alternative":
                model.Add(sum(child_vars) >= 1).OnlyEnforceIf(parent_var)
                model.Add(sum(child_vars) <= 1).OnlyEnforceIf(parent_var)
            elif group_type == "or":
                if min_card is None:
                    min_card = 1
                if min_card > 0:
                    model.Add(sum(child_vars) >= min_card).OnlyEnforceIf(parent_var)
                if max_card is not None:
                    model.Add(sum(child_vars) <= max_card).OnlyEnforceIf(parent_var)

        # Constraints binarias
        name_to_id = self._build_feature_name_map(features)
        for constraint in constraints:
            expr_text = constraint.get("expr_text", "")
            parsed = self._parse_binary_constraint(expr_text, name_to_id)
            if not parsed:
                continue
            ctype, left_id, right_id = parsed
            left_id = self._resolve_feature_id(left_id, name_to_id)
            right_id = self._resolve_feature_id(right_id, name_to_id)
            if left_id not in vars_map or right_id not in vars_map:
                continue
            if ctype in {"requires", "implies"}:
                model.AddImplication(vars_map[left_id], vars_map[right_id])
            elif ctype == "excludes":
                model.Add(vars_map[left_id] + vars_map[right_id] <= 1)

        # Decisiones parciales
        if partial_selection:
            for fid, selected in partial_selection.items():
                fid_str = str(fid)
                if fid_str in vars_map:
                    model.Add(vars_map[fid_str] == (1 if selected else 0))

        model.Maximize(sum(vars_map.values()))
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return GenerationResult(
                success=False,
                errors=["No se encontró configuración válida"],
            )

        selected = [fid for fid, var in vars_map.items() if solver.Value(var) == 1]
        configuration = {fid: fid in selected for fid in vars_map.keys()}
        return GenerationResult(
            success=True,
            configuration=configuration,
            selected_features=selected,
            score=self._score_configuration(configuration, list(configuration.keys())),
            iterations=0,
        )

    def _generate_cp_sat_multiple(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        count: int,
        partial_selection: Optional[Dict[str, bool]] = None,
    ) -> List[GenerationResult]:
        """
        Genera múltiples configuraciones usando CP-SAT (OR-Tools).
        """
        if not CP_SAT_AVAILABLE:
            return [
                GenerationResult(
                    success=False,
                    errors=["OR-Tools no disponible (instalar ortools)"],
                )
            ]

        self._initialize(features, relations, constraints)
        model = cp_model.CpModel()
        vars_map = {
            fid: model.NewBoolVar(f"f_{fid}") for fid in self.features_map.keys()
        }

        for feature in features:
            if feature.get("parent_id") is None:
                fid = str(feature.get("id"))
                if fid in vars_map:
                    model.Add(vars_map[fid] == 1)

        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = relation.get("relation_type")
            if parent_id not in vars_map or child_id not in vars_map:
                continue
            if relation_type == "mandatory":
                model.AddImplication(vars_map[parent_id], vars_map[child_id])
            elif relation_type == "optional":
                model.AddImplication(vars_map[child_id], vars_map[parent_id])

        groups = self._build_groups_from_relations(relations)
        for group in groups:
            parent_id = group["parent_id"]
            child_ids = group["children"]
            group_type = group["group_type"]
            min_card = group["min_cardinality"]
            max_card = group["max_cardinality"]

            if parent_id not in vars_map:
                continue
            parent_var = vars_map[parent_id]
            child_vars = [vars_map[cid] for cid in child_ids if cid in vars_map]
            if not child_vars:
                continue

            for child_var in child_vars:
                model.AddImplication(child_var, parent_var)

            if group_type == "alternative":
                model.Add(sum(child_vars) >= 1).OnlyEnforceIf(parent_var)
                model.Add(sum(child_vars) <= 1).OnlyEnforceIf(parent_var)
            elif group_type == "or":
                if min_card is None:
                    min_card = 1
                if min_card > 0:
                    model.Add(sum(child_vars) >= min_card).OnlyEnforceIf(parent_var)
                if max_card is not None:
                    model.Add(sum(child_vars) <= max_card).OnlyEnforceIf(parent_var)

        name_to_id = self._build_feature_name_map(features)
        for constraint in constraints:
            expr_text = constraint.get("expr_text", "")
            parsed = self._parse_binary_constraint(expr_text, name_to_id)
            if not parsed:
                continue
            ctype, left_id, right_id = parsed
            left_id = self._resolve_feature_id(left_id, name_to_id)
            right_id = self._resolve_feature_id(right_id, name_to_id)
            if left_id not in vars_map or right_id not in vars_map:
                continue
            if ctype in {"requires", "implies"}:
                model.AddImplication(vars_map[left_id], vars_map[right_id])
            elif ctype == "excludes":
                model.Add(vars_map[left_id] + vars_map[right_id] <= 1)

        if partial_selection:
            for fid, selected in partial_selection.items():
                fid_str = str(fid)
                if fid_str in vars_map:
                    model.Add(vars_map[fid_str] == (1 if selected else 0))

        class _SolutionCollector(cp_model.CpSolverSolutionCallback):
            def __init__(self, variables: dict[str, "cp_model.BoolVar"], limit: int):
                super().__init__()
                self.variables = variables
                self.limit = limit
                self.solutions: list[list[str]] = []

            def on_solution_callback(self) -> None:
                selected_local = [
                    fid for fid, var in self.variables.items() if self.Value(var) == 1
                ]
                self.solutions.append(selected_local)
                if len(self.solutions) >= self.limit:
                    self.StopSearch()

        solver = cp_model.CpSolver()
        collector = _SolutionCollector(vars_map, count)
        solver.SearchForAllSolutions(model, collector)

        results: list[GenerationResult] = []
        for selected in collector.solutions:
            configuration = {fid: fid in selected for fid in vars_map.keys()}
            results.append(
                GenerationResult(
                    success=True,
                    configuration=configuration,
                    selected_features=selected,
                    score=self._score_configuration(
                        configuration, list(configuration.keys())
                    ),
                    iterations=0,
                )
            )

        if not results:
            return [
                GenerationResult(
                    success=False,
                    errors=["No se encontró configuración válida"],
                )
            ]

        return results

    def _build_feature_name_map(
        self, features: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        name_to_id: Dict[str, str] = {}
        for feature in features:
            feature_id = str(feature.get("id"))
            name = feature.get("name", feature_id)
            name_to_id[name.strip().lower()] = feature_id
        return name_to_id

    def _resolve_feature_id(self, token: str, name_to_id: Dict[str, str]) -> str:
        normalized = token.strip().lower()
        return name_to_id.get(normalized, token.strip())

    def _parse_binary_constraint(
        self, expr_text: str, name_to_id: Dict[str, str]
    ) -> Optional[tuple[str, str, str]]:
        expr_upper = expr_text.upper()
        if "REQUIRES" in expr_upper:
            idx = expr_upper.index("REQUIRES")
            left = expr_text[:idx]
            right = expr_text[idx + len("REQUIRES") :]
            return "requires", left.strip(), right.strip()
        if "EXCLUDES" in expr_upper:
            idx = expr_upper.index("EXCLUDES")
            left = expr_text[:idx]
            right = expr_text[idx + len("EXCLUDES") :]
            return "excludes", left.strip(), right.strip()
        if "IMPLIES" in expr_upper:
            idx = expr_upper.index("IMPLIES")
            left = expr_text[:idx]
            right = expr_text[idx + len("IMPLIES") :]
            return "implies", left.strip(), right.strip()
        return None

    def _build_groups_from_relations(
        self, relations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        groups: Dict[str, Dict[str, Any]] = {}
        for relation in relations:
            group_id = relation.get("group_id")
            if not group_id:
                continue
            gid = str(group_id)
            group = groups.get(gid)
            if not group:
                group = {
                    "parent_id": str(relation.get("parent_id")),
                    "children": [],
                    "group_type": relation.get("group_type"),
                    "min_cardinality": relation.get("min_cardinality"),
                    "max_cardinality": relation.get("max_cardinality"),
                }
                groups[gid] = group
            child_id = relation.get("child_id")
            if child_id:
                group["children"].append(str(child_id))

        return list(groups.values())

    def _generate_sat_enumeration(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        partial_selection: Optional[Dict[str, bool]] = None,
    ) -> GenerationResult:
        """
        Genera una configuración válida usando enumeración SAT/SMT (Z3).
        """
        validator = FeatureModelLogicalValidator()
        try:
            solutions = validator.enumerate_configurations(
                features=features,
                relations=relations,
                constraints=constraints,
                max_solutions=1,
                partial_selection=partial_selection,
            )
        except Exception as exc:
            return GenerationResult(success=False, errors=[str(exc)])

        if not solutions:
            return GenerationResult(
                success=False,
                errors=["No se encontró configuración válida"],
            )

        selected = solutions[0]
        configuration = {
            str(feature.get("id")): str(feature.get("id")) in selected
            for feature in features
        }
        return GenerationResult(
            success=True,
            configuration=configuration,
            selected_features=selected,
            score=self._score_configuration(configuration, list(configuration.keys())),
            iterations=0,
        )

    def _initialize(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> None:
        """Inicializa estructuras internas."""
        signature = (
            tuple(sorted(str(f.get("id")) for f in features)),
            tuple(
                sorted(
                    (
                        str(r.get("parent_id")),
                        str(r.get("child_id")),
                        str(r.get("relation_type")),
                        str(r.get("group_id")),
                    )
                    for r in relations
                )
            ),
            tuple(
                sorted((str(c.get("id")), str(c.get("expr_text"))) for c in constraints)
            ),
        )

        if self._model_signature == signature:
            return

        self._model_signature = signature
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
