# Motor de Validación de Feature Models

Este módulo implementa los **tres componentes fundamentales** del motor de validación para Feature Models, basados en técnicas de Ingeniería de Líneas de Productos de Software (SPL).

## 📋 Componentes del Sistema

### 1. 🔍 Validador Lógico (SAT/SMT Solver)

**Archivo:** `logical_validator.py`

**Responsabilidad:**
Verifica la consistencia global de las decisiones tomadas sobre un Feature Model, incluyendo restricciones booleanas, cardinalidades, relaciones cross-tree y condiciones derivadas.

**Tecnologías utilizadas:**

- ✅ **SymPy**: Para representación simbólica y evaluación lógica de restricciones
- 🔮 **PySAT** (futuro): Para resolución SAT de alto rendimiento
- 🔮 **Z3** (futuro): Para SMT y optimización avanzada

**Funcionalidades principales:**

```python
from app.services.validation import LogicalValidator

validator = LogicalValidator()

# Validar un Feature Model completo
result = validator.validate_feature_model(
    features=features,
    relations=relations,
    constraints=constraints
)

# Validar una configuración específica
result = validator.validate_configuration(
    features=features,
    relations=relations,
    constraints=constraints,
    selected_features=["feature1", "feature2", "feature3"]
)

print(f"Válido: {result.is_valid}")
print(f"Errores: {result.errors}")
print(f"Asignación: {result.satisfying_assignment}")
```

**Qué valida:**

- ✅ Consistencia de restricciones booleanas
- ✅ Relaciones parent-child (mandatory, optional)
- ✅ Relaciones cross-tree (requires, excludes, implies)
- ✅ Cardinalidades de grupos (or-group, xor-group)
- ✅ Satisfacibilidad global del modelo
- ✅ Detección de contradicciones

---

### 2. 🎲 Generador de Configuraciones (Heurístico / Búsqueda Guiada)

**Archivo:** `configuration_generator.py`

**Responsabilidad:**
Construye configuraciones válidas a partir del modelo, ya sea para derivar productos completos o proponer alternativas viables ante decisiones parciales.

**Tecnologías utilizadas:**

- ✅ **Búsqueda heurística**: Greedy, Random, Beam Search
- 🔮 **DEAP** (futuro): Algoritmos genéticos para optimización
- ✅ **Integración con validador**: Verifica corrección de configuraciones generadas

**Estrategias disponibles:**

```python
from app.services.validation import ConfigurationGenerator, GenerationStrategy

generator = ConfigurationGenerator()

# Generar configuración con estrategia greedy
result = generator.generate_valid_configuration(
    features=features,
    relations=relations,
    constraints=constraints,
    strategy=GenerationStrategy.GREEDY
)

# Completar configuración parcial del usuario
result = generator.complete_partial_configuration(
    features=features,
    relations=relations,
    constraints=constraints,
    partial_selection={"feature1": True, "feature2": False}
)

# Generar múltiples configuraciones diversas
results = generator.generate_multiple_configurations(
    features=features,
    relations=relations,
    constraints=constraints,
    count=10,
    diverse=True
)
```

**Estrategias implementadas:**

- ✅ **GREEDY**: Selección golosa por prioridad (rápida, determinista)
- ✅ **RANDOM**: Selección aleatoria válida (diversidad, no determinista)
- 🔮 **BEAM_SEARCH**: Búsqueda en haz (explora múltiples caminos)
- 🔮 **GENETIC**: Algoritmos genéticos (optimización multi-objetivo)

---

### 3. 📊 Analizador Estructural (Grafos y Optimización)

**Archivo:** `structural_analyzer.py`

**Responsabilidad:**
Inspecciona propiedades internas del Feature Model que dependen de la topología del modelo, no solo de restricciones lógicas.

**Tecnologías utilizadas:**

- ✅ **Algoritmos de grafos**: DFS, análisis de alcanzabilidad
- 🔮 **NetworkX** (futuro): Para análisis avanzado de grafos
- ✅ **Tarjan's SCC**: Detección de componentes fuertemente conexas (ciclos)

**Tipos de análisis:**

```python
from app.services.validation import StructuralAnalyzer, AnalysisType

analyzer = StructuralAnalyzer()

# Análisis completo
results = analyzer.analyze_feature_model(
    features=features,
    relations=relations,
    constraints=constraints,
    analysis_types=[
        AnalysisType.DEAD_FEATURES,
        AnalysisType.REDUNDANCIES,
        AnalysisType.COMPLEXITY_METRICS
    ]
)

# Detectar solo dead features
dead_features = analyzer.detect_dead_features(
    features=features,
    relations=relations,
    constraints=constraints
)

# Calcular impacto de una feature
impact = analyzer.calculate_feature_impact(
    features=features,
    relations=relations,
    constraints=constraints,
    feature_id="feature_uuid"
)

print(f"Features afectadas: {impact['transitive_dependents']}")
print(f"Score de impacto: {impact['impact_score']}")
```

**Análisis implementados:**

| Análisis                    | Descripción                                                 | Utilidad              |
| --------------------------- | ----------------------------------------------------------- | --------------------- |
| **DEAD_FEATURES**           | Detecta features inaccesibles desde la raíz                 | Limpieza del modelo   |
| **REDUNDANCIES**            | Encuentra relaciones y constraints duplicados               | Simplificación        |
| **IMPLICIT_RELATIONS**      | Identifica dependencias implícitas derivadas de constraints | Documentación         |
| **TRANSITIVE_DEPENDENCIES** | Calcula cierre transitivo de dependencias                   | Análisis de impacto   |
| **STRONGLY_CONNECTED**      | Detecta ciclos en el grafo de dependencias                  | Corrección de errores |
| **COMPLEXITY_METRICS**      | Calcula profundidad, ramificación, densidad                 | Métricas de calidad   |

---

## 🚀 Ejemplo de Uso Completo

```python
from app.services.validation import (
    LogicalValidator,
    ConfigurationGenerator,
    StructuralAnalyzer,
    GenerationStrategy,
    AnalysisType
)

# ========== 1. ANÁLISIS ESTRUCTURAL ==========
print("=== ANÁLISIS ESTRUCTURAL ===")
analyzer = StructuralAnalyzer()
structural_results = analyzer.analyze_feature_model(
    features=my_features,
    relations=my_relations,
    constraints=my_constraints
)

# Revisar dead features
dead_features_result = structural_results[AnalysisType.DEAD_FEATURES]
print(f"Features muertas encontradas: {len(dead_features_result.issues)}")
for issue in dead_features_result.issues:
    print(f"  - {issue.description}")

# Revisar métricas de complejidad
metrics_result = structural_results[AnalysisType.COMPLEXITY_METRICS]
print(f"Métricas del modelo:")
print(f"  - Profundidad máxima: {metrics_result.metrics['max_depth']}")
print(f"  - Total features: {metrics_result.metrics['total_features']}")
print(f"  - Factor ramificación: {metrics_result.metrics['avg_branching_factor']}")
print(f"  - Densidad constraints: {metrics_result.metrics['constraint_density']}")


# ========== 2. VALIDACIÓN LÓGICA ==========
print("\n=== VALIDACIÓN LÓGICA ===")
validator = LogicalValidator()
validation_result = validator.validate_feature_model(
    features=my_features,
    relations=my_relations,
    constraints=my_constraints
)

if validation_result.is_valid:
    print("✅ El modelo es CONSISTENTE y SATISFACIBLE")
    print(f"Ejemplo de asignación válida: {validation_result.satisfying_assignment}")
else:
    print("❌ El modelo tiene ERRORES:")
    for error in validation_result.errors:
        print(f"  - {error}")


# ========== 3. GENERACIÓN DE CONFIGURACIONES ==========
print("\n=== GENERACIÓN DE CONFIGURACIONES ===")
generator = ConfigurationGenerator()

# Generar 5 configuraciones válidas
configs = generator.generate_multiple_configurations(
    features=my_features,
    relations=my_relations,
    constraints=my_constraints,
    count=5,
    diverse=True
)

print(f"Se generaron {len(configs)} configuraciones válidas:")
for i, config in enumerate(configs):
    print(f"  Config {i+1}: {len(config.selected_features)} features seleccionadas")
    print(f"    Score: {config.score:.2f}")


# ========== 4. VALIDAR CONFIGURACIÓN DE USUARIO ==========
print("\n=== VALIDACIÓN DE CONFIGURACIÓN ESPECÍFICA ===")
user_selection = ["feature1_uuid", "feature2_uuid", "feature3_uuid"]

validation_result = validator.validate_configuration(
    features=my_features,
    relations=my_relations,
    constraints=my_constraints,
    selected_features=user_selection
)

if validation_result.is_valid:
    print("✅ La configuración del usuario es VÁLIDA")
else:
    print("❌ La configuración del usuario es INVÁLIDA:")
    for error in validation_result.errors:
        print(f"  - {error}")

    # Intentar completar/corregir automáticamente
    print("\n🔧 Intentando generar configuración alternativa...")
    corrected = generator.complete_partial_configuration(
        features=my_features,
        relations=my_relations,
        constraints=my_constraints,
        partial_selection={fid: True for fid in user_selection}
    )

    if corrected.success:
        print("✅ Se encontró una configuración válida cercana:")
        print(f"   Features: {corrected.selected_features}")
```

---

## 📦 Dependencias

### Actuales (implementado)

```toml
# backend/pyproject.toml
dependencies = [
    "sympy>=1.12",  # Álgebra simbólica
]
```

### Futuras (roadmap)

```toml
dependencies = [
    "python-sat>=0.1.8.dev13",  # SAT solving industrial
    "z3-solver>=4.12.2.0",       # SMT solving (Microsoft Research)
    "networkx>=3.2",             # Análisis avanzado de grafos
    "deap>=1.4.1",               # Algoritmos genéticos
]
```

---

## 🏗️ Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────┐
│              API LAYER (FastAPI Endpoints)              │
│  POST /validate/model     GET /analyze/structure        │
│  POST /validate/config    POST /generate/configuration  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                 VALIDATION SERVICE LAYER                │
│                                                          │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────┐│
│  │   Logical      │  │  Configuration   │  │Structural││
│  │   Validator    │◄─┤   Generator      │  │ Analyzer ││
│  │                │  │                  │  │          ││
│  │ • SymPy        │  │ • Greedy         │  │ • DFS    ││
│  │ • PySAT (fut.) │  │ • Random         │  │ • SCC    ││
│  │ • Z3 (fut.)    │  │ • Beam (fut.)    │  │ • Metrics││
│  └────────────────┘  └──────────────────┘  └──────────┘│
└──────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│              DOMAIN LAYER (Models & Repos)              │
│  Feature, FeatureRelation, Constraint, Configuration    │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Notas de Implementación

### Estado Actual (v1.0)

**✅ Implementado:**

- Validador Lógico básico con SymPy
- Generador con estrategias Greedy y Random
- Analizador estructural con detección de dead features
- Métricas de complejidad
- Detección de redundancias básicas

**⚠️ Limitaciones actuales:**

- Parser de constraints simplificado (solo REQUIRES/EXCLUDES/IMPLIES)
- Tarjan SCC no completamente implementado
- No se usan solvers SAT industriales todavía
- Generador BEAM_SEARCH es placeholder
- No hay soporte para algoritmos genéticos

### Roadmap v2.0

1. **Integrar PySAT para validación formal:**

   ```python
   from pysat.solvers import Glucose3
   # Resolver SAT en lugar de SymPy para modelos grandes
   ```

2. **Agregar NetworkX para análisis avanzado:**

   ```python
   import networkx as nx
   # Usar algoritmos optimizados de grafos
   ```

3. **Implementar Beam Search completo:**

   - Mantener top-k candidatos
   - Scoring function personalizable

4. **Añadir DEAP para algoritmos genéticos:**

   ```python
   from deap import algorithms, base, creator, tools
   # Evolucionar configuraciones óptimas
   ```

5. **Parser robusto de constraints:**
   - Soporte completo para CNF/DNF
   - Uso de `expr_cnf` almacenado en BD

---

## 🔬 Referencias Teóricas

Este motor de validación implementa técnicas descritas en:

- Benavides, D. et al. (2010). "Automated analysis of feature models 20 years later: A literature review"
- Zhao, Y. et al. (2018). "PySAT: A Python Toolkit for Prototyping with SAT Oracles"
- De Moura, L. & Bjørner, N. (2008). "Z3: An Efficient SMT Solver"
- Meurer, A. et al. (2017). "SymPy: symbolic computing in Python"

---

## 👥 Contribución

Para agregar nuevas estrategias de validación o generación:

1. Crear nueva clase heredando de las interfaces base
2. Implementar métodos requeridos
3. Registrar en el factory pattern correspondiente
4. Agregar tests unitarios

---

## 📄 Licencia

Este módulo es parte del proyecto Feature Model y sigue la misma licencia del proyecto principal.
