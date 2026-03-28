"""
Componente 1: Validador Lógico (SAT/SMT Solver) - 3 Niveles

Responsable de verificar la consistencia global de las decisiones tomadas sobre un FM,
incluyendo restricciones booleanas, cardinalidades, relaciones cross-tree y condiciones derivadas.

Tecnologías:
- Nivel 1 (Básico): SymPy - Validación simbólica para modelos pequeños
- Nivel 2 (Industrial): PySAT - SAT solving escalable para modelos medianos/grandes
- Nivel 3 (Avanzado): Z3 - SMT, Max-SAT y optimización para análisis complejos

El validador selecciona automáticamente el nivel apropiado según el tamaño del modelo.
"""

from typing import Dict, List, Tuple, Any, Optional
from itertools import combinations
from enum import Enum

# Nivel 1: SymPy (Básico)
import sympy
from sympy.logic.boolalg import to_cnf
from sympy.logic.inference import satisfiable
from sympy import symbols, And, Or, Not, Implies

# Nivel 2: PySAT (Industrial)
try:
    from pysat.solvers import Glucose3, Minisat22
    from pysat.formula import CNF

    PYSAT_AVAILABLE = True
except ImportError:
    PYSAT_AVAILABLE = False

# Nivel 3: Z3 (Avanzado)
try:
    import z3

    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False

from app.exceptions import (
    InvalidConstraintException,
    UnsatisfiableConstraintException,
    ConflictingConstraintsException,
    InvalidConfigurationException,
    MandatoryFeatureMissingException,
    ExcludedFeaturesSelectedException,
    RequiredFeatureMissingException,
)


class ValidationLevel(Enum):
    """Nivel de validación a utilizar."""

    SYMPY = "sympy"  # Nivel 1: Básico, modelos pequeños (<50 features)
    PYSAT = "pysat"  # Nivel 2: Industrial, modelos medianos/grandes (50-1000 features)
    Z3 = "z3"  # Nivel 3: Avanzado, optimización y SMT (análisis complejos)


class FeatureModelValidationResult:
    """Resultado de una validación."""

    def __init__(
        self,
        is_valid: bool,
        errors: List[str] | None = None,
        warnings: List[str] | None = None,
        satisfying_assignment: Dict[str, bool] | None = None,
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.satisfying_assignment = satisfying_assignment


class FeatureModelLogicalValidator:
    """
    Validador Lógico basado en satisfacibilidad (SAT/SMT) - 3 Niveles.

    Verifica:
    - Consistencia de restricciones booleanas
    - Relaciones parent-child (mandatory, optional)
    - Relaciones cross-tree (requires, excludes, implies)
    - Cardinalidades de grupos (or-group, xor-group)
    - Satisfacibilidad global del modelo

    Niveles de validación:
    - SYMPY: Modelos pequeños (<50 features), validación simbólica
    - PYSAT: Modelos medianos/grandes (50-1000 features), SAT industrial
    - Z3: Análisis avanzados, optimización, Max-SAT, SMT
    """

    def __init__(self, validation_level: ValidationLevel | None = None):
        """
        Inicializa el validador lógico.

        Args:
            validation_level: Nivel de validación a usar. Si es None, se selecciona automáticamente
                            según el tamaño del modelo.
        """
        self.validation_level = validation_level
        self.var_mapping: Dict[str, sympy.Symbol] = {}
        self.constraints: List[sympy.Basic] = []

        # Mapeo para PySAT (feature_id -> variable_id)
        self.pysat_var_mapping: Dict[str, int] = {}
        self.pysat_reverse_mapping: Dict[int, str] = {}
        self.pysat_cnf: CNF | None = None if not PYSAT_AVAILABLE else CNF()

        # Z3 solver
        self.z3_solver: z3.Solver | None = None if not Z3_AVAILABLE else z3.Solver()
        self.z3_var_mapping: Dict[str, z3.Bool] = {}

    def _select_validation_level(self, num_features: int) -> ValidationLevel:
        """
        Selecciona automáticamente el nivel de validación según el tamaño del modelo.

        Args:
            num_features: Número de features en el modelo

        Returns:
            ValidationLevel apropiado
        """
        if self.validation_level:
            return self.validation_level

        # Selección automática basada en tamaño y disponibilidad
        if num_features < 50:
            # Modelos pequeños: SymPy es suficiente
            return ValidationLevel.SYMPY
        elif num_features < 1000 and PYSAT_AVAILABLE:
            # Modelos medianos/grandes: PySAT es ideal
            return ValidationLevel.PYSAT
        elif Z3_AVAILABLE:
            # Modelos muy grandes o si PySAT no está disponible
            return ValidationLevel.Z3
        else:
            # Fallback a SymPy si no hay nada más
            return ValidationLevel.SYMPY

    def validate_feature_model(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> FeatureModelValidationResult:
        """
        Valida un Feature Model completo usando el nivel apropiado.

        Args:
            features: Lista de features con sus propiedades
            relations: Lista de relaciones entre features
            constraints: Lista de restricciones cross-tree

        Returns:
            FeatureModelValidationResult con el resultado de la validación

        Raises:
            UnsatisfiableConstraintException: Si el modelo es globalmente insatisfacible
        """
        self._reset()

        # Seleccionar nivel de validación
        level = self._select_validation_level(len(features))

        # Delegar a la implementación específica
        if level == ValidationLevel.PYSAT and PYSAT_AVAILABLE:
            return self._validate_with_pysat(features, relations, constraints)
        elif level == ValidationLevel.Z3 and Z3_AVAILABLE:
            return self._validate_with_z3(features, relations, constraints)
        else:
            # Fallback a SymPy (implementación original)
            return self._validate_with_sympy(features, relations, constraints)

    def _validate_with_sympy(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> FeatureModelValidationResult:
        """Validación Nivel 1: SymPy (implementación original)."""
        errors = []
        warnings = []

        # 1. Crear variables simbólicas para cada feature
        self._build_symbolic_variables(features)

        # 2. Codificar relaciones jerárquicas y grupos
        hierarchy_constraints = self._encode_hierarchy(features, relations)
        group_constraints = self._encode_groups_sympy(features, relations)
        self.constraints.extend(hierarchy_constraints)
        self.constraints.extend(group_constraints)

        # 3. Codificar constraints cross-tree
        cross_tree_constraints, constraint_errors = self._encode_cross_tree_constraints(
            constraints
        )
        self.constraints.extend(cross_tree_constraints)
        errors.extend(constraint_errors)

        # 4. Verificar satisfacibilidad
        is_satisfiable, assignment = self._check_satisfiability()

        if not is_satisfiable:
            raise UnsatisfiableConstraintException(
                constraint_description="El modelo completo"
            )

        # 5. Verificar contradicciones obvias
        contradictions = self._detect_contradictions()
        if contradictions:
            warnings.extend([f"Contradicción detectada: {c}" for c in contradictions])

        return FeatureModelValidationResult(
            is_valid=is_satisfiable and len(errors) == 0,
            errors=errors,
            warnings=warnings,
            satisfying_assignment=assignment,
        )

    def _validate_with_pysat(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> FeatureModelValidationResult:
        """
        Validación Nivel 2: PySAT (SAT solving industrial).

        Más escalable que SymPy para modelos medianos/grandes.
        """
        errors = []
        warnings = []

        # 1. Construir mapeo de variables (feature_id -> int)
        for idx, feature in enumerate(features, start=1):
            feature_id = str(feature.get("id"))
            self.pysat_var_mapping[feature_id] = idx
            self.pysat_reverse_mapping[idx] = feature_id

        # 2. Inicializar CNF
        if self.pysat_cnf is None:
            self.pysat_cnf = CNF()
        else:
            self.pysat_cnf.clauses = []

        # 3. Codificar relaciones jerárquicas
        self._encode_hierarchy_pysat(features, relations)

        # 4. Codificar grupos OR/XOR
        self._encode_groups_pysat(features, relations)

        # 5. Codificar constraints cross-tree
        constraint_errors = self._encode_cross_tree_constraints_pysat(
            features, constraints
        )
        errors.extend(constraint_errors)

        # 6. Resolver SAT
        try:
            solver = Glucose3()
            solver.append_formula(self.pysat_cnf.clauses)
            sat = solver.solve()
            if not sat:
                raise UnsatisfiableConstraintException(
                    constraint_description="El modelo completo"
                )
            model = solver.get_model()
            assignment = self._convert_pysat_assignment(model)
            solver.delete()
        except UnsatisfiableConstraintException:
            raise
        except Exception as exc:
            errors.append(f"PySAT error: {exc}")
            assignment = None

        return FeatureModelValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            satisfying_assignment=assignment,
        )

    def _validate_with_z3(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> FeatureModelValidationResult:
        """
        Validación Nivel 3: Z3 (SMT, Max-SAT, optimización).

        Permite análisis más avanzados y optimización.
        """
        errors = []
        warnings = []

        # 1. Construir variables Z3
        self.z3_solver = z3.Solver()
        self.z3_var_mapping = {}
        for feature in features:
            feature_id = str(feature.get("id"))
            self.z3_var_mapping[feature_id] = z3.Bool(feature_id)

        # 2. Codificar relaciones jerárquicas
        self._encode_hierarchy_z3(features, relations)

        # 3. Codificar grupos OR/XOR
        self._encode_groups_z3(features, relations)

        # 4. Codificar constraints cross-tree
        constraint_errors = self._encode_cross_tree_constraints_z3(
            features, constraints
        )
        errors.extend(constraint_errors)

        # 5. Resolver
        if self.z3_solver.check() != z3.sat:
            raise UnsatisfiableConstraintException(
                constraint_description="El modelo completo"
            )

        model = self.z3_solver.model()
        assignment = self._convert_z3_assignment(model)

        return FeatureModelValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            satisfying_assignment=assignment,
        )

    def validate_configuration(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        selected_features: List[str],
    ) -> FeatureModelValidationResult:
        """
        Valida una configuración específica (selección de features).

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones
            constraints: Lista de restricciones
            selected_features: IDs de features seleccionadas

        Returns:
            FeatureModelValidationResult indicando si la configuración es válida

        Raises:
            InvalidConfigurationException: Si la configuración seleccionada es inválida
        """
        self._reset()

        # Seleccionar nivel de validación
        level = self._select_validation_level(len(features))

        if level == ValidationLevel.PYSAT and PYSAT_AVAILABLE:
            return self._validate_configuration_with_pysat(
                features, relations, constraints, selected_features
            )
        if level == ValidationLevel.Z3 and Z3_AVAILABLE:
            return self._validate_configuration_with_z3(
                features, relations, constraints, selected_features
            )

        return self._validate_configuration_with_sympy(
            features, relations, constraints, selected_features
        )

    def _reset(self) -> None:
        """Reinicia el estado interno del validador."""
        self.var_mapping = {}
        self.constraints = []
        self.pysat_var_mapping = {}
        self.pysat_reverse_mapping = {}
        self.pysat_cnf = CNF() if PYSAT_AVAILABLE else None
        self.z3_solver = z3.Solver() if Z3_AVAILABLE else None
        self.z3_var_mapping = {}

    def _build_symbolic_variables(self, features: List[Dict[str, Any]]) -> None:
        """Crea una variable booleana SymPy por cada feature."""
        for feature in features:
            feature_id = str(feature.get("id"))
            feature_name = feature.get("name", feature_id)
            # Crear símbolo usando el nombre limpio
            clean_name = feature_name.replace(" ", "_").replace("-", "_")
            self.var_mapping[feature_id] = symbols(clean_name, bool=True)

    def _encode_hierarchy(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> List[sympy.Basic]:
        """
        Codifica las relaciones jerárquicas como fórmulas lógicas.

        Reglas:
        - Mandatory: parent => child
        - Optional: ninguna restricción adicional (child puede o no estar)
        - Root: debe estar siempre seleccionada
        """
        constraints = []

        # Encontrar el root
        roots = [f for f in features if f.get("parent_id") is None]
        for root in roots:
            root_id = str(root.get("id"))
            if root_id in self.var_mapping:
                constraints.append(self.var_mapping[root_id])  # Root siempre activa

        # Codificar relaciones parent-child
        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = relation.get("relation_type")

            if parent_id not in self.var_mapping or child_id not in self.var_mapping:
                continue

            parent_var = self.var_mapping[parent_id]
            child_var = self.var_mapping[child_id]

            if relation_type == "mandatory":
                # Parent implica Child: P => C equivale a (¬P ∨ C)
                constraints.append(Implies(parent_var, child_var))
            elif relation_type == "optional":
                # Child implica Parent: C => P
                constraints.append(Implies(child_var, parent_var))
            # or-group y xor-group requieren manejo de grupos (ver _encode_groups)

        return constraints

    def _encode_groups_sympy(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> List[sympy.Basic]:
        """Codificar grupos OR/XOR con SymPy."""
        constraints: list[sympy.Basic] = []
        groups = self._collect_groups(features, relations)
        for group in groups:
            parent_id = group["parent_id"]
            children_ids = group["children"]
            group_type = group["group_type"]
            min_card = group["min_cardinality"]
            max_card = group["max_cardinality"]

            if parent_id not in self.var_mapping:
                continue
            parent_var = self.var_mapping[parent_id]
            child_vars = [
                self.var_mapping[cid] for cid in children_ids if cid in self.var_mapping
            ]
            if not child_vars:
                continue

            # Child -> Parent
            for child_var in child_vars:
                constraints.append(Implies(child_var, parent_var))

            # Parent -> cardinality
            if group_type == "alternative":
                constraints.append(Implies(parent_var, Or(*child_vars)))
                for c1, c2 in combinations(child_vars, 2):
                    constraints.append(Implies(parent_var, Not(And(c1, c2))))
            elif group_type == "or":
                if min_card is None:
                    min_card = 1
                if min_card <= 1:
                    constraints.append(Implies(parent_var, Or(*child_vars)))
                else:
                    constraints.extend(
                        self._sympy_at_least(parent_var, child_vars, min_card)
                    )
                if max_card is not None:
                    constraints.extend(
                        self._sympy_at_most(parent_var, child_vars, max_card)
                    )

        return constraints

    def _encode_cross_tree_constraints(
        self, constraints: List[Dict[str, Any]]
    ) -> Tuple[List[sympy.Basic], List[str]]:
        """
        Codifica constraints cross-tree (requires, excludes, implies).

        Returns:
            Tupla (lista de constraints simbólicas, lista de errores)

        Raises:
            InvalidConstraintException: Si una constraint no puede ser parseada
        """
        symbolic_constraints = []
        errors = []

        for constraint in constraints:
            expr_text = constraint.get("expr_text", "")

            try:
                symbolic_expr = None
                if expr_text:
                    symbolic_expr = self._parse_constraint_expression(expr_text)

                if symbolic_expr:
                    symbolic_constraints.append(symbolic_expr)
                else:
                    raise InvalidConstraintException(
                        expression=expr_text,
                        reason="Formato de constraint no reconocido o features no encontradas",
                    )
            except InvalidConstraintException:
                raise
            except Exception as e:
                raise InvalidConstraintException(
                    expression=expr_text,
                    reason=f"Error durante el parseo: {str(e)}",
                )

        return symbolic_constraints, errors

    def _encode_hierarchy_pysat(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> None:
        """Codifica jerarquía en CNF para PySAT."""
        # Root siempre activa
        roots = [f for f in features if f.get("parent_id") is None]
        for root in roots:
            root_id = str(root.get("id"))
            var = self.pysat_var_mapping.get(root_id)
            if var:
                self.pysat_cnf.append([var])

        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = relation.get("relation_type")

            parent_var = self.pysat_var_mapping.get(parent_id)
            child_var = self.pysat_var_mapping.get(child_id)
            if not parent_var or not child_var:
                continue

            if relation_type == "mandatory":
                self.pysat_cnf.append([-parent_var, child_var])
            elif relation_type == "optional":
                self.pysat_cnf.append([-child_var, parent_var])

    def _encode_groups_pysat(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> None:
        """Codifica grupos OR/XOR en CNF para PySAT."""
        groups = self._collect_groups(features, relations)
        for group in groups:
            parent_id = group["parent_id"]
            children_ids = group["children"]
            group_type = group["group_type"]
            min_card = group["min_cardinality"]
            max_card = group["max_cardinality"]

            parent_var = self.pysat_var_mapping.get(parent_id)
            child_vars = [self.pysat_var_mapping.get(cid) for cid in children_ids]
            child_vars = [v for v in child_vars if v]
            if not parent_var or not child_vars:
                continue

            # Child -> Parent
            for child_var in child_vars:
                self.pysat_cnf.append([-child_var, parent_var])

            if group_type == "alternative":
                # Parent -> al menos uno
                self.pysat_cnf.append([-parent_var] + child_vars)
                # Parent -> a lo sumo uno
                for c1, c2 in combinations(child_vars, 2):
                    self.pysat_cnf.append([-parent_var, -c1, -c2])
            elif group_type == "or":
                if min_card is None:
                    min_card = 1
                if min_card <= 1:
                    self.pysat_cnf.append([-parent_var] + child_vars)
                else:
                    self._pysat_at_least(parent_var, child_vars, min_card)
                if max_card is not None:
                    self._pysat_at_most(parent_var, child_vars, max_card)

    def _encode_cross_tree_constraints_pysat(
        self, features: List[Dict[str, Any]], constraints: List[Dict[str, Any]]
    ) -> List[str]:
        """Codifica constraints cross-tree en CNF para PySAT."""
        errors = []
        name_to_id = self._build_feature_name_map(features)

        for constraint in constraints:
            expr_text = constraint.get("expr_text", "")
            expr_cnf = constraint.get("expr_cnf")

            if expr_cnf:
                clauses = self._normalize_expr_cnf(expr_cnf)
                if clauses:
                    for clause in clauses:
                        self.pysat_cnf.append(clause)
                    continue

            if expr_text:
                parsed = self._parse_binary_constraint(expr_text, name_to_id)
                if parsed:
                    ctype, left_id, right_id = parsed
                    left_var = self.pysat_var_mapping.get(left_id)
                    right_var = self.pysat_var_mapping.get(right_id)
                    if not left_var or not right_var:
                        continue
                    if ctype == "requires" or ctype == "implies":
                        self.pysat_cnf.append([-left_var, right_var])
                    elif ctype == "excludes":
                        self.pysat_cnf.append([-left_var, -right_var])
                    continue

            errors.append(f"Constraint no soportada para CNF: '{expr_text}'")

        return errors

    def _encode_hierarchy_z3(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> None:
        """Codifica jerarquía con Z3."""
        # Root siempre activa
        roots = [f for f in features if f.get("parent_id") is None]
        for root in roots:
            root_id = str(root.get("id"))
            root_var = self.z3_var_mapping.get(root_id)
            if root_var is not None:
                self.z3_solver.add(root_var)

        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = relation.get("relation_type")

            parent_var = self.z3_var_mapping.get(parent_id)
            child_var = self.z3_var_mapping.get(child_id)
            if parent_var is None or child_var is None:
                continue

            if relation_type == "mandatory":
                self.z3_solver.add(z3.Implies(parent_var, child_var))
            elif relation_type == "optional":
                self.z3_solver.add(z3.Implies(child_var, parent_var))

    def _encode_groups_z3(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> None:
        """Codifica grupos OR/XOR con Z3."""
        groups = self._collect_groups(features, relations)
        for group in groups:
            parent_id = group["parent_id"]
            children_ids = group["children"]
            group_type = group["group_type"]
            min_card = group["min_cardinality"]
            max_card = group["max_cardinality"]

            parent_var = self.z3_var_mapping.get(parent_id)
            child_vars = [self.z3_var_mapping.get(cid) for cid in children_ids]
            child_vars = [v for v in child_vars if v is not None]
            if parent_var is None or not child_vars:
                continue

            # Child -> Parent
            for child_var in child_vars:
                self.z3_solver.add(z3.Implies(child_var, parent_var))

            if group_type == "alternative":
                self.z3_solver.add(z3.Implies(parent_var, z3.Or(*child_vars)))
                self.z3_solver.add(
                    z3.Implies(
                        parent_var,
                        z3.PbEq([(c, 1) for c in child_vars], 1),
                    )
                )
            elif group_type == "or":
                if min_card is None:
                    min_card = 1
                if min_card > 0:
                    self.z3_solver.add(
                        z3.Implies(
                            parent_var,
                            z3.PbGe([(c, 1) for c in child_vars], min_card),
                        )
                    )
                if max_card is not None:
                    self.z3_solver.add(
                        z3.Implies(
                            parent_var,
                            z3.PbLe([(c, 1) for c in child_vars], max_card),
                        )
                    )

    def _encode_cross_tree_constraints_z3(
        self, features: List[Dict[str, Any]], constraints: List[Dict[str, Any]]
    ) -> List[str]:
        """Codifica constraints cross-tree con Z3."""
        errors = []
        name_to_id = self._build_feature_name_map(features)

        for constraint in constraints:
            expr_text = constraint.get("expr_text", "")

            if expr_text:
                parsed = self._parse_binary_constraint(expr_text, name_to_id)
                if parsed:
                    ctype, left_id, right_id = parsed
                    left_var = self.z3_var_mapping.get(left_id)
                    right_var = self.z3_var_mapping.get(right_id)
                    if left_var is None or right_var is None:
                        continue
                    if ctype == "requires" or ctype == "implies":
                        self.z3_solver.add(z3.Implies(left_var, right_var))
                    elif ctype == "excludes":
                        self.z3_solver.add(z3.Not(z3.And(left_var, right_var)))
                    continue

            errors.append(f"Constraint no soportada para Z3: '{expr_text}'")

        return errors

    def _validate_configuration_with_sympy(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        selected_features: List[str],
    ) -> FeatureModelValidationResult:
        """Validación de configuración con SymPy."""
        # 1. Construir variables y constraints del modelo
        self._build_symbolic_variables(features)
        hierarchy_constraints = self._encode_hierarchy(features, relations)
        group_constraints = self._encode_groups_sympy(features, relations)
        cross_tree_constraints, _ = self._encode_cross_tree_constraints(constraints)

        all_constraints = (
            hierarchy_constraints + group_constraints + cross_tree_constraints
        )

        # 2. Agregar las decisiones del usuario como constraints
        user_decisions = []
        for feature_id, symbol in self.var_mapping.items():
            if feature_id in selected_features:
                user_decisions.append(symbol)
            else:
                user_decisions.append(Not(symbol))

        # 3. Combinar todo y verificar satisfacibilidad
        full_formula = And(*all_constraints, *user_decisions)

        try:
            result = satisfiable(full_formula)
            if result is False:
                violated = self._identify_violated_constraints(
                    all_constraints, user_decisions
                )
                violated_msg = (
                    "; ".join(violated) if violated else "restricciones del modelo"
                )
                raise InvalidConfigurationException(
                    configuration_details=f"Configuración con {len(selected_features)} features seleccionadas",
                    reason=violated_msg,
                )
            return FeatureModelValidationResult(
                is_valid=True,
                satisfying_assignment=self._convert_assignment(result),
            )
        except InvalidConfigurationException:
            raise
        except Exception as e:
            raise InvalidConfigurationException(
                configuration_details=f"{len(selected_features)} features seleccionadas",
                reason=f"Error durante validación: {str(e)}",
            )

    def _validate_configuration_with_pysat(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        selected_features: List[str],
    ) -> FeatureModelValidationResult:
        """Validación de configuración con PySAT."""
        # Construir CNF base
        for idx, feature in enumerate(features, start=1):
            feature_id = str(feature.get("id"))
            self.pysat_var_mapping[feature_id] = idx
            self.pysat_reverse_mapping[idx] = feature_id

        if self.pysat_cnf is None:
            self.pysat_cnf = CNF()
        else:
            self.pysat_cnf.clauses = []

        self._encode_hierarchy_pysat(features, relations)
        self._encode_groups_pysat(features, relations)
        self._encode_cross_tree_constraints_pysat(features, constraints)

        # Aplicar decisiones del usuario
        for feature_id, var in self.pysat_var_mapping.items():
            if feature_id in selected_features:
                self.pysat_cnf.append([var])
            else:
                self.pysat_cnf.append([-var])

        solver = Minisat22()
        solver.append_formula(self.pysat_cnf.clauses)
        if not solver.solve():
            raise InvalidConfigurationException(
                configuration_details=f"Configuración con {len(selected_features)} features seleccionadas",
                reason="restricciones del modelo",
            )
        model = solver.get_model()
        assignment = self._convert_pysat_assignment(model)
        solver.delete()

        return FeatureModelValidationResult(
            is_valid=True, satisfying_assignment=assignment
        )

    def _validate_configuration_with_z3(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        selected_features: List[str],
    ) -> FeatureModelValidationResult:
        """Validación de configuración con Z3."""
        self.z3_solver = z3.Solver()
        self.z3_var_mapping = {}
        for feature in features:
            feature_id = str(feature.get("id"))
            self.z3_var_mapping[feature_id] = z3.Bool(feature_id)

        self._encode_hierarchy_z3(features, relations)
        self._encode_groups_z3(features, relations)
        self._encode_cross_tree_constraints_z3(features, constraints)

        for feature_id, var in self.z3_var_mapping.items():
            if feature_id in selected_features:
                self.z3_solver.add(var)
            else:
                self.z3_solver.add(z3.Not(var))

        if self.z3_solver.check() != z3.sat:
            raise InvalidConfigurationException(
                configuration_details=f"Configuración con {len(selected_features)} features seleccionadas",
                reason="restricciones del modelo",
            )
        model = self.z3_solver.model()
        assignment = self._convert_z3_assignment(model)

        return FeatureModelValidationResult(
            is_valid=True, satisfying_assignment=assignment
        )

    def _convert_pysat_assignment(self, model: List[int]) -> Dict[str, bool]:
        """Convierte asignación de PySAT a dict feature_id -> bool."""
        assignment = {}
        if not model:
            return assignment
        for lit in model:
            var_id = abs(lit)
            feature_id = self.pysat_reverse_mapping.get(var_id)
            if feature_id:
                assignment[feature_id] = lit > 0
        return assignment

    def _convert_z3_assignment(self, model: "z3.ModelRef") -> Dict[str, bool]:
        """Convierte modelo Z3 a dict feature_id -> bool."""
        assignment = {}
        for feature_id, var in self.z3_var_mapping.items():
            val = model.evaluate(var, model_completion=True)
            assignment[feature_id] = bool(z3.is_true(val))
        return assignment

    def _build_feature_name_map(self, features: List[Dict[str, Any]]) -> Dict[str, str]:
        """Mapea nombres normalizados a feature_id."""
        name_to_id = {}
        for feature in features:
            feature_id = str(feature.get("id"))
            name = feature.get("name", feature_id)
            normalized = name.strip().lower()
            name_to_id[normalized] = feature_id
        return name_to_id

    def _parse_binary_constraint(
        self, expr_text: str, name_to_id: Dict[str, str]
    ) -> Optional[Tuple[str, str, str]]:
        """Parsea constraints binarias REQUIRES/EXCLUDES/IMPLIES."""
        expr_upper = expr_text.upper()
        if "REQUIRES" in expr_upper:
            parts = expr_upper.split("REQUIRES", 1)
            idx = expr_upper.index("REQUIRES")
            left = expr_text[:idx]
            right = expr_text[idx + len("REQUIRES") :]
            return (
                "requires",
                self._resolve_feature_id(left, name_to_id),
                self._resolve_feature_id(right, name_to_id),
            )
        if "EXCLUDES" in expr_upper:
            idx = expr_upper.index("EXCLUDES")
            left = expr_text[:idx]
            right = expr_text[idx + len("EXCLUDES") :]
            return (
                "excludes",
                self._resolve_feature_id(left, name_to_id),
                self._resolve_feature_id(right, name_to_id),
            )
        if "IMPLIES" in expr_upper:
            idx = expr_upper.index("IMPLIES")
            left = expr_text[:idx]
            right = expr_text[idx + len("IMPLIES") :]
            return (
                "implies",
                self._resolve_feature_id(left, name_to_id),
                self._resolve_feature_id(right, name_to_id),
            )
        return None

    def _resolve_feature_id(self, token: str, name_to_id: Dict[str, str]) -> str:
        """Resuelve ID desde nombre o token."""
        normalized = token.strip().lower()
        return name_to_id.get(normalized, token.strip())

    def _normalize_expr_cnf(self, expr_cnf: Any) -> Optional[List[List[int]]]:
        """Normaliza expr_cnf a lista de cláusulas."""
        if isinstance(expr_cnf, dict):
            clauses = expr_cnf.get("clauses")
            return clauses if isinstance(clauses, list) else None
        if isinstance(expr_cnf, list):
            return expr_cnf
        return None

    def _collect_groups(
        self, features: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recolecta definición de grupos OR/XOR desde features/relaciones."""
        groups: Dict[str, Dict[str, Any]] = {}

        # Grupos inferidos desde features con group_id y group info
        for feature in features:
            group_id = feature.get("group_id")
            if not group_id:
                continue
            group = feature.get("group") or {}
            parent_id = (
                str(feature.get("parent_id")) if feature.get("parent_id") else None
            )
            key = str(group_id)
            if key not in groups:
                groups[key] = {
                    "parent_id": parent_id,
                    "children": [],
                    "group_type": group.get("group_type"),
                    "min_cardinality": group.get("min_cardinality", 1),
                    "max_cardinality": group.get("max_cardinality"),
                }
            groups[key]["children"].append(str(feature.get("id")))

        # Grupos inferidos desde relaciones con group_type o relation_type
        for relation in relations:
            parent_id = str(relation.get("parent_id"))
            child_id = str(relation.get("child_id"))
            relation_type = (relation.get("relation_type") or "").lower()
            group_type = (relation.get("group_type") or "").lower()
            group_id = relation.get("group_id")

            candidate = group_type or relation_type
            if candidate in {"xor", "alternative", "or"}:
                normalized_type = (
                    "alternative" if candidate in {"xor", "alternative"} else "or"
                )
                key = str(group_id) if group_id else f"{parent_id}:{normalized_type}"
                if key not in groups:
                    groups[key] = {
                        "parent_id": parent_id,
                        "children": [],
                        "group_type": normalized_type,
                        "min_cardinality": relation.get("min_cardinality", 1),
                        "max_cardinality": relation.get("max_cardinality"),
                    }
                groups[key]["children"].append(child_id)

        # Normalizar grupos
        normalized = []
        for group in groups.values():
            if not group.get("group_type"):
                continue
            if not group.get("parent_id"):
                continue
            normalized.append(group)
        return normalized

    def _sympy_at_least(
        self, parent_var: sympy.Symbol, vars_list: List[sympy.Symbol], k: int
    ) -> List[sympy.Basic]:
        """Codifica al menos k con SymPy (CNF directa)."""
        constraints = []
        n = len(vars_list)
        if k <= 0 or k > n:
            return constraints
        subset_size = n - k + 1
        for subset in combinations(vars_list, subset_size):
            constraints.append(Implies(parent_var, Or(*subset)))
        return constraints

    def _sympy_at_most(
        self, parent_var: sympy.Symbol, vars_list: List[sympy.Symbol], k: int
    ) -> List[sympy.Basic]:
        """Codifica a lo sumo k con SymPy (CNF directa)."""
        constraints = []
        n = len(vars_list)
        if k < 0 or k >= n:
            return constraints
        for subset in combinations(vars_list, k + 1):
            constraints.append(Implies(parent_var, Or(*[Not(v) for v in subset])))
        return constraints

    def _pysat_at_least(self, parent_var: int, vars_list: List[int], k: int) -> None:
        n = len(vars_list)
        if k <= 0 or k > n:
            return
        subset_size = n - k + 1
        for subset in combinations(vars_list, subset_size):
            self.pysat_cnf.append([-parent_var] + list(subset))

    def _pysat_at_most(self, parent_var: int, vars_list: List[int], k: int) -> None:
        n = len(vars_list)
        if k < 0 or k >= n:
            return
        for subset in combinations(vars_list, k + 1):
            clause = [-parent_var] + [-v for v in subset]
            self.pysat_cnf.append(clause)

    def _parse_constraint_expression(self, expr_text: str) -> Optional[sympy.Basic]:
        """
        Parsea una expresión textual de constraint a fórmula SymPy.

        Soporta:
        - A REQUIRES B => (A => B)
        - A EXCLUDES B => ¬(A ∧ B) = (¬A ∨ ¬B)
        - A IMPLIES B => (A => B)

        TODO: Implementar parser más robusto o usar el expr_cnf existente
        """
        # Simplificación: esta es una implementación básica
        # En producción, usar el campo expr_cnf que ya está en la BD
        expr_upper = expr_text.upper()

        # Extraer nombres de features (esto es un ejemplo simplificado)
        # En producción, deberías parsear correctamente
        if "REQUIRES" in expr_upper:
            idx = expr_upper.index("REQUIRES")
            left_text = expr_text[:idx].strip()
            right_text = expr_text[idx + len("REQUIRES") :].strip()
            left = self._find_var_by_name(left_text)
            right = self._find_var_by_name(right_text)
            if left and right:
                return Implies(left, right)

        elif "EXCLUDES" in expr_upper:
            idx = expr_upper.index("EXCLUDES")
            left_text = expr_text[:idx].strip()
            right_text = expr_text[idx + len("EXCLUDES") :].strip()
            left = self._find_var_by_name(left_text)
            right = self._find_var_by_name(right_text)
            if left and right:
                return Or(Not(left), Not(right))

        elif "IMPLIES" in expr_upper:
            idx = expr_upper.index("IMPLIES")
            left_text = expr_text[:idx].strip()
            right_text = expr_text[idx + len("IMPLIES") :].strip()
            left = self._find_var_by_name(left_text)
            right = self._find_var_by_name(right_text)
            if left and right:
                return Implies(left, right)

        return None

    def _find_var_by_name(self, name: str) -> Optional[sympy.Symbol]:
        """Encuentra una variable simbólica por nombre."""
        clean_name = name.replace(" ", "_").replace("-", "_")
        for var in self.var_mapping.values():
            if str(var) == clean_name:
                return var
        return None

    def _check_satisfiability(self) -> Tuple[bool, Optional[Dict[str, bool]]]:
        """
        Verifica si el conjunto de constraints es satisfacible.

        Returns:
            Tupla (es_satisfacible, asignación_de_ejemplo)
        """
        if not self.constraints:
            return True, None

        try:
            formula = And(*self.constraints)
            result = satisfiable(formula)

            if result is False:
                return False, None
            elif isinstance(result, dict):
                # Convertir asignación de SymPy a dict legible
                assignment = self._convert_assignment(result)
                return True, assignment
            else:
                return True, None
        except Exception:
            return False, None

    def _convert_assignment(
        self, sympy_assignment: Dict[sympy.Symbol, bool]
    ) -> Dict[str, bool]:
        """Convierte asignación de SymPy a diccionario feature_id -> bool."""
        result = {}
        for feature_id, symbol in self.var_mapping.items():
            if symbol in sympy_assignment:
                result[feature_id] = sympy_assignment[symbol]
        return result

    def _detect_contradictions(self) -> List[str]:
        """
        Detecta contradicciones obvias en las constraints.

        Busca pares de constraints que se contradigan directamente.

        Raises:
            ConflictingConstraintsException: Si se detectan constraints contradictorias
        """
        contradictions = []

        # Simplificar cada constraint y buscar pares (C, ¬C)
        simplified = []
        for c in self.constraints:
            try:
                simp = sympy.simplify(c)
                simplified.append(simp)
            except Exception:
                pass

        # Buscar contradicciones
        for i, c1 in enumerate(simplified):
            for c2 in simplified[i + 1 :]:
                try:
                    # Verificar si c1 y c2 son contradictorios
                    combined = And(c1, c2)
                    if satisfiable(combined) is False:
                        contradiction_msg = f"{c1} contradice {c2}"
                        contradictions.append(contradiction_msg)
                        # Lanzar excepción si detectamos contradicción
                        raise ConflictingConstraintsException(
                            constraint1=str(c1), constraint2=str(c2)
                        )
                except ConflictingConstraintsException:
                    # Re-lanzar excepciones personalizadas
                    raise
                except Exception:
                    pass

        return contradictions

    def _identify_violated_constraints(
        self, model_constraints: List[sympy.Basic], user_decisions: List[sympy.Basic]
    ) -> List[str]:
        """
        Identifica qué restricciones específicas son violadas por la configuración.

        Raises:
            MandatoryFeatureMissingException: Si falta una feature mandatory
            ExcludedFeaturesSelectedException: Si hay features mutuamente excluyentes seleccionadas
            RequiredFeatureMissingException: Si falta una feature requerida por otra
        """
        violated = []

        # Verificar cada constraint individualmente con las decisiones del usuario
        user_formula = And(*user_decisions)

        for constraint in model_constraints:
            combined = And(user_formula, constraint)
            try:
                if satisfiable(combined) is False:
                    violated.append(f"Restricción violada: {constraint}")

                    # Intentar determinar el tipo específico de violación
                    constraint_str = str(constraint)

                    # Si es una implicación (mandatory o required)
                    if "Implies" in constraint_str:
                        # Parsear las features involucradas
                        raise RequiredFeatureMissingException(
                            requiring_feature="Feature requerida",
                            required_feature="Feature dependiente",
                        )
                    # Si es una disyunción negada (excludes)
                    elif "Or" in constraint_str and "Not" in constraint_str:
                        raise ExcludedFeaturesSelectedException(
                            feature1="Feature A", feature2="Feature B"
                        )

            except (RequiredFeatureMissingException, ExcludedFeaturesSelectedException):
                # Re-lanzar excepciones específicas
                raise
            except Exception:
                pass

        return violated

    def check_mandatory_features(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        selected_features: List[str],
    ) -> None:
        """
        Verifica que todas las features mandatory estén seleccionadas.

        Args:
            features: Lista de features del modelo
            relations: Lista de relaciones
            selected_features: IDs de features seleccionadas

        Raises:
            MandatoryFeatureMissingException: Si falta alguna feature mandatory
        """
        # Encontrar features mandatory cuyo parent está seleccionado
        for relation in relations:
            if relation.get("relation_type") == "mandatory":
                parent_id = str(relation.get("parent_id"))
                child_id = str(relation.get("child_id"))

                # Si el parent está seleccionado, el child debe estarlo también
                if parent_id in selected_features and child_id not in selected_features:
                    # Buscar nombres de features para el mensaje
                    parent_name = next(
                        (
                            f.get("name")
                            for f in features
                            if str(f.get("id")) == parent_id
                        ),
                        parent_id,
                    )
                    child_name = next(
                        (
                            f.get("name")
                            for f in features
                            if str(f.get("id")) == child_id
                        ),
                        child_id,
                    )

                    raise MandatoryFeatureMissingException(
                        parent_feature=parent_name, mandatory_feature=child_name
                    )

    def check_excluded_features(
        self, constraints: List[Dict[str, Any]], selected_features: List[str]
    ) -> None:
        """
        Verifica que no haya features mutuamente excluyentes seleccionadas.

        Args:
            constraints: Lista de restricciones del modelo
            selected_features: IDs de features seleccionadas

        Raises:
            ExcludedFeaturesSelectedException: Si hay features excluyentes seleccionadas
        """
        for constraint in constraints:
            expr_text = constraint.get("expr_text", "")

            if "EXCLUDES" in expr_text.upper():
                # Parsear las features involucradas
                parts = expr_text.split(" EXCLUDES ")
                if len(parts) == 2:
                    feature1 = parts[0].strip()
                    feature2 = parts[1].strip()

                    # Verificar si ambas están seleccionadas
                    # Esto es simplificado - necesitaría mapear nombres a IDs
                    raise ExcludedFeaturesSelectedException(
                        feature1=feature1, feature2=feature2
                    )
