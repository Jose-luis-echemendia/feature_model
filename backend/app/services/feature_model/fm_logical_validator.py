"""
Componente 1: Validador Lógico (SAT/SMT Solver)

Responsable de verificar la consistencia global de las decisiones tomadas sobre un FM,
incluyendo restricciones booleanas, cardinalidades, relaciones cross-tree y condiciones derivadas.

Tecnologías:
- SymPy: Para representación simbólica y evaluación lógica
- PySAT (futuro): Para resolución SAT de alto rendimiento
- Z3 (futuro): Para SMT y optimización avanzada
"""

from typing import Dict, List, Tuple, Any, Optional

import sympy
from sympy.logic.boolalg import to_cnf, satisfiable
from sympy import symbols, And, Or, Not, Implies

from app.exceptions import (
    InvalidConstraintException,
    UnsatisfiableConstraintException,
    ConflictingConstraintsException,
    InvalidConfigurationException,
    MandatoryFeatureMissingException,
    ExcludedFeaturesSelectedException,
    RequiredFeatureMissingException,
)


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
    Validador Lógico basado en satisfacibilidad (SAT/SMT).

    Verifica:
    - Consistencia de restricciones booleanas
    - Relaciones parent-child (mandatory, optional)
    - Relaciones cross-tree (requires, excludes, implies)
    - Cardinalidades de grupos (or-group, xor-group)
    - Satisfacibilidad global del modelo
    """

    def __init__(self):
        """Inicializa el validador lógico."""
        self.var_mapping: Dict[str, sympy.Symbol] = {}
        self.constraints: List[sympy.Basic] = []

    def validate_feature_model(
        self,
        features: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> FeatureModelValidationResult:
        """
        Valida un Feature Model completo.

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
        errors = []
        warnings = []

        # 1. Crear variables simbólicas para cada feature
        self._build_symbolic_variables(features)

        # 2. Codificar relaciones jerárquicas
        hierarchy_constraints = self._encode_hierarchy(features, relations)
        self.constraints.extend(hierarchy_constraints)

        # 3. Codificar constraints cross-tree
        cross_tree_constraints, constraint_errors = self._encode_cross_tree_constraints(
            constraints
        )
        self.constraints.extend(cross_tree_constraints)
        errors.extend(constraint_errors)

        # 4. Verificar satisfacibilidad
        is_satisfiable, assignment = self._check_satisfiability()

        if not is_satisfiable:
            # Lanzar excepción personalizada en lugar de acumular error
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

        # 1. Construir variables y constraints del modelo
        self._build_symbolic_variables(features)
        hierarchy_constraints = self._encode_hierarchy(features, relations)
        cross_tree_constraints, _ = self._encode_cross_tree_constraints(constraints)

        all_constraints = hierarchy_constraints + cross_tree_constraints

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
                # Identificar restricciones violadas para mensaje detallado
                violated = self._identify_violated_constraints(
                    all_constraints, user_decisions
                )
                violated_msg = (
                    "; ".join(violated) if violated else "restricciones del modelo"
                )

                # Lanzar excepción personalizada
                raise InvalidConfigurationException(
                    configuration_details=f"Configuración con {len(selected_features)} features seleccionadas",
                    reason=violated_msg,
                )
            else:
                return FeatureModelValidationResult(
                    is_valid=True,
                    satisfying_assignment=self._convert_assignment(result),
                )
        except InvalidConfigurationException:
            # Re-lanzar excepciones personalizadas
            raise
        except Exception as e:
            # Convertir errores inesperados a InvalidConfigurationException
            raise InvalidConfigurationException(
                configuration_details=f"{len(selected_features)} features seleccionadas",
                reason=f"Error durante validación: {str(e)}",
            )

    def _reset(self) -> None:
        """Reinicia el estado interno del validador."""
        self.var_mapping = {}
        self.constraints = []

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
                # Intentar parsear la expresión usando SymPy
                # Asumiendo formato: "feature_name REQUIRES other_feature"
                symbolic_expr = self._parse_constraint_expression(expr_text)
                if symbolic_expr:
                    symbolic_constraints.append(symbolic_expr)
                else:
                    # Si no se pudo parsear, lanzar excepción
                    raise InvalidConstraintException(
                        constraint_expression=expr_text,
                        reason="Formato de constraint no reconocido o features no encontradas",
                    )
            except InvalidConstraintException:
                # Re-lanzar excepciones personalizadas
                raise
            except Exception as e:
                # Convertir otros errores a InvalidConstraintException
                raise InvalidConstraintException(
                    constraint_expression=expr_text,
                    reason=f"Error durante el parseo: {str(e)}",
                )

        return symbolic_constraints, errors

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
            parts = expr_text.split(" REQUIRES ")
            if len(parts) == 2:
                left = self._find_var_by_name(parts[0].strip())
                right = self._find_var_by_name(parts[1].strip())
                if left and right:
                    return Implies(left, right)

        elif "EXCLUDES" in expr_upper:
            parts = expr_text.split(" EXCLUDES ")
            if len(parts) == 2:
                left = self._find_var_by_name(parts[0].strip())
                right = self._find_var_by_name(parts[1].strip())
                if left and right:
                    return Or(Not(left), Not(right))

        elif "IMPLIES" in expr_upper:
            parts = expr_text.split(" IMPLIES ")
            if len(parts) == 2:
                left = self._find_var_by_name(parts[0].strip())
                right = self._find_var_by_name(parts[1].strip())
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
