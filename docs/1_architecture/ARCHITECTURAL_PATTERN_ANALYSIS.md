# 🏛️ Análisis del Patrón Arquitectónico y Motor de Validación

> **Fecha**: 9 de diciembre de 2025  
> **Proyecto**: Feature Models Platform - Backend  
> **Enfoque**: Identificación de patrón arquitectónico actual + Integración del motor de validación

---

## 📐 Patrón Arquitectónico Identificado

### **Arquitectura Actual: Híbrida Estratificada (Layered + Plugin-based)**

Basado en el análisis del código y la estructura del proyecto, el backend implementa una **arquitectura híbrida** que combina:

#### 1. **Arquitectura en Capas (Layered Architecture)** - Predominante

```
┌─────────────────────────────────────────────────┐
│  CAPA DE PRESENTACIÓN (API Layer)              │
│  - FastAPI Endpoints                            │
│  - Request/Response Handling                    │
│  - Dependency Injection                         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  CAPA DE APLICACIÓN (Application/Service Layer)│
│  - Business Logic                               │
│  - Orchestration Services                       │
│  - Feature Flags                                │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  CAPA DE DOMINIO (Domain Layer)                │
│  - Feature Models (Domain Objects)              │
│  - Feature Trees & Constraints                  │
│  - Validation Rules                             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  CAPA DE ACCESO A DATOS (Data Access Layer)    │
│  - Repository Pattern (Sync/Async)              │
│  - Database Abstraction                         │
│  - ORM (SQLModel)                               │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  CAPA DE INFRAESTRUCTURA (Infrastructure)       │
│  - PostgreSQL                                   │
│  - Redis Cache                                  │
│  - S3/MinIO Storage                             │
└─────────────────────────────────────────────────┘
```

#### 2. **Arquitectura de Plugins (Elementos Presentes)**

```
┌──────────────────────────────────────────────┐
│         CORE APPLICATION                     │
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │ Repository │  │ Service    │            │
│  │ Interfaces │  │ Interfaces │            │
│  └────────────┘  └────────────┘            │
│        ↑               ↑                     │
└────────┼───────────────┼─────────────────────┘
         │               │
    ┌────┴───────┐  ┌───┴─────────┐
    │ Sync       │  │ Async       │
    │ Impl.      │  │ Impl.       │
    └────────────┘  └─────────────┘
         PLUGINS (Intercambiables)
```

**Elementos de Plugin Architecture presentes:**

- ✅ Interfaces bien definidas (`Protocol`)
- ✅ Múltiples implementaciones intercambiables (sync/async)
- ✅ Dependency Injection para selección en runtime
- ❌ **Falta**: Plugin registry formal
- ❌ **Falta**: Dynamic plugin loading

#### 3. **Elementos de Microkernel Architecture**

El patrón Microkernel (o Plugin Architecture avanzado) también está presente parcialmente:

```
     ┌─────────────────────────────┐
     │   MINIMAL CORE SYSTEM       │
     │  - FastAPI Application      │
     │  - Dependency Injection     │
     │  - Base Models              │
     └─────────────────────────────┘
              ↑      ↑      ↑
              │      │      │
        ┌─────┘      │      └─────┐
        │            │            │
    ┌───────┐  ┌─────────┐  ┌─────────┐
    │ Redis │  │   S3    │  │ Celery  │
    │Service│  │ Service │  │ Tasks   │
    └───────┘  └─────────┘  └─────────┘
     EXTERNAL PLUGINS (Services)
```

---

## 🎯 Clasificación Definitiva

### **Patrón Principal: Arquitectura en Capas (Layered Architecture)**

**Justificación:**

1. ✅ Clara separación en capas (`api/`, `services/`, `models/`, `repositories/`, `core/`)
2. ✅ Dependencias unidireccionales (top-down)
3. ✅ Cada capa tiene responsabilidades bien definidas
4. ✅ Comunicación entre capas mediante interfaces
5. ✅ Aislamiento de infraestructura

**Variante específica:** **Clean Architecture / Hexagonal Architecture (Ports & Adapters)**

```
┌──────────────────────────────────────────────────┐
│          APPLICATION CORE (Domain)               │
│  - Feature Models                                │
│  - Business Rules                                │
│  - Validation Logic                              │
└──────────────────────────────────────────────────┘
              ↑                    ↑
              │                    │
     ┌────────┴────────┐   ┌───────┴────────┐
     │  INPUT PORTS    │   │  OUTPUT PORTS  │
     │  (Interfaces)   │   │  (Interfaces)  │
     └─────────────────┘   └────────────────┘
              ↑                    ↑
              │                    │
     ┌────────┴────────┐   ┌───────┴────────┐
     │   ADAPTERS      │   │   ADAPTERS     │
     │ - API (FastAPI) │   │ - Repositories │
     │ - CLI           │   │ - External APIs│
     └─────────────────┘   └────────────────┘
```

**Evidencia en el código:**

```python
# PORTS (Interfaces/Protocols)
class IDomainRepositoryAsync(Protocol):
    async def create(self, data: DomainCreate) -> Domain: ...
    async def get(self, domain_id: UUID) -> Optional[Domain]: ...

# ADAPTERS (Implementaciones concretas)
class DomainRepositoryAsync(BaseDomainRepository, IDomainRepositoryAsync):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: DomainCreate) -> Domain:
        # Implementación específica de PostgreSQL
        ...

# APPLICATION CORE (Domain)
class Domain(BaseTable, DomainBase, table=True):
    """Modelo de dominio puro"""
    __tablename__ = "domains"

    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
```

---

## 🔧 Integración del Motor de Validación

### **Ubicación Arquitectónica de los 3 Componentes**

Los tres componentes del motor de validación se integran en la **Capa de Aplicación/Servicios**, creando un **subsistema especializado**:

```
┌──────────────────────────────────────────────────────────┐
│              CAPA DE PRESENTACIÓN (API)                  │
│  /api/v1/validation/                                     │
│  /api/v1/configuration/                                  │
│  /api/v1/analysis/                                       │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│          CAPA DE APLICACIÓN (Services)                   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │      🔍 MOTOR DE VALIDACIÓN (Subsistema)           │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ 1️⃣ VALIDADOR LÓGICO (SAT/SMT Solver)        │ │ │
│  │  │  - python-sat (PySAT)                       │ │ │
│  │  │  - z3-solver                                │ │ │
│  │  │  - Validación de constraints                │ │ │
│  │  │  - Verificación de consistencia             │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ 2️⃣ GENERADOR DE CONFIGURACIONES             │ │ │
│  │  │  - Algoritmos genéticos (DEAP)              │ │ │
│  │  │  - Beam search                              │ │ │
│  │  │  - Random sampling guiado                   │ │ │
│  │  │  - Integración con SAT solver               │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ 3️⃣ ANALIZADOR ESTRUCTURAL                   │ │ │
│  │  │  - NetworkX (análisis de grafos)            │ │ │
│  │  │  - Dead features detection                  │ │ │
│  │  │  - Componentes fuertemente conexas          │ │ │
│  │  │  - Métricas de impacto                      │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│              CAPA DE DOMINIO (Models)                    │
│  - Feature, FeatureModel, Constraint, Configuration      │
└──────────────────────────────────────────────────────────┘
```

---

## 📚 Stack Tecnológico Recomendado por Componente

### 1️⃣ **Validador Lógico (SAT/SMT Solver)**

#### **Librerías Recomendadas:**

| Librería               | Uso Principal           | Ventajas                                                                              | Instalación              |
| ---------------------- | ----------------------- | ------------------------------------------------------------------------------------- | ------------------------ |
| **python-sat** (PySAT) | ⭐ SAT solving primario | - Múltiples solvers (Glucose, MiniSat)<br>- API Pythonic<br>- Excelente documentación | `pip install python-sat` |
| **z3-solver**          | SMT solving avanzado    | - Teorías combinadas<br>- Optimización<br>- Microsoft Research                        | `pip install z3-solver`  |
| **pycosat**            | SAT solving ligero      | - Muy rápido<br>- Mínimas dependencias                                                | `pip install pycosat`    |

#### **Recomendación Principal: python-sat (PySAT)**

**Justificación:**

- ✅ Diseñado específicamente para Python
- ✅ Soporte para CNF/DNF
- ✅ Múltiples backends de solvers
- ✅ API de alto nivel y bajo nivel
- ✅ Usado en investigación de SPL

**Ejemplo de integración:**

```python
# backend/app/services/validation/sat_validator.py

from pysat.solvers import Glucose3
from pysat.formula import CNF
from typing import List, Tuple, Set
from app.models import Feature, Constraint, Configuration

class SATValidator:
    """Validador lógico usando SAT solver."""

    def __init__(self):
        self.solver = None
        self.var_mapping = {}  # feature_id -> SAT variable

    def build_cnf_from_feature_model(
        self,
        features: List[Feature],
        constraints: List[Constraint]
    ) -> CNF:
        """Convierte un Feature Model a formato CNF."""
        cnf = CNF()
        var_counter = 1

        # 1. Mapear features a variables SAT
        for feature in features:
            self.var_mapping[str(feature.id)] = var_counter
            var_counter += 1

        # 2. Codificar jerarquía (parent-child)
        for feature in features:
            if feature.parent_id:
                parent_var = self.var_mapping[str(feature.parent_id)]
                child_var = self.var_mapping[str(feature.id)]

                # Si parent está seleccionado y feature es MANDATORY
                if feature.type == FeatureType.MANDATORY:
                    # parent → child (equivalente a: ¬parent ∨ child)
                    cnf.append([-parent_var, child_var])

                # child → parent (si hijo está, padre debe estar)
                cnf.append([-child_var, parent_var])

        # 3. Codificar grupos (OR/XOR)
        for feature in features:
            if feature.feature_group_id:
                # Implementar cardinalidad del grupo
                # min <= seleccionados <= max
                pass  # Ver implementación completa abajo

        # 4. Codificar cross-tree constraints
        for constraint in constraints:
            source_var = self.var_mapping[str(constraint.source_feature_id)]
            target_var = self.var_mapping[str(constraint.target_feature_id)]

            if constraint.type == ConstraintType.REQUIRES:
                # source → target: ¬source ∨ target
                cnf.append([-source_var, target_var])

            elif constraint.type == ConstraintType.EXCLUDES:
                # source ∧ target = false: ¬source ∨ ¬target
                cnf.append([-source_var, -target_var])

        return cnf

    async def validate_configuration(
        self,
        configuration: Configuration,
        feature_model_version_id: UUID
    ) -> Tuple[bool, List[str]]:
        """
        Valida si una configuración es válida según el FM.

        Returns:
            (is_valid, error_messages)
        """
        # 1. Obtener FM y constraints
        features = await self._get_features(feature_model_version_id)
        constraints = await self._get_constraints(feature_model_version_id)

        # 2. Construir CNF del modelo
        cnf = self.build_cnf_from_feature_model(features, constraints)

        # 3. Agregar decisiones del usuario como cláusulas unitarias
        selected_ids = configuration.selected_feature_ids
        for feature_id in selected_ids:
            var = self.var_mapping.get(str(feature_id))
            if var:
                cnf.append([var])  # Forzar que esté seleccionada

        # 4. Resolver con SAT solver
        solver = Glucose3()
        solver.append_formula(cnf)

        is_satisfiable = solver.solve()

        if not is_satisfiable:
            # Encontrar conflicto (core insatisfacible)
            errors = self._diagnose_conflicts(solver, configuration)
            return False, errors

        return True, []

    async def is_feature_model_consistent(
        self,
        feature_model_version_id: UUID
    ) -> Tuple[bool, str]:
        """
        Verifica si el FM es consistente (tiene al menos una configuración válida).
        """
        features = await self._get_features(feature_model_version_id)
        constraints = await self._get_constraints(feature_model_version_id)

        cnf = self.build_cnf_from_feature_model(features, constraints)

        solver = Glucose3()
        solver.append_formula(cnf)

        if solver.solve():
            return True, "Feature Model es consistente"
        else:
            return False, "Feature Model es inconsistente - no tiene configuraciones válidas"
```

---

### 2️⃣ **Generador de Configuraciones**

#### **Librerías Recomendadas:**

| Librería           | Uso Principal           | Ventajas                                                    | Instalación           |
| ------------------ | ----------------------- | ----------------------------------------------------------- | --------------------- |
| **DEAP**           | ⭐ Algoritmos genéticos | - Framework completo GA<br>- Flexible<br>- Bien documentado | `pip install deap`    |
| **scipy.optimize** | Optimización general    | - Parte de SciPy<br>- Múltiples algoritmos                  | Incluido en scipy     |
| **ortools**        | Constraint Programming  | - Google OR-Tools<br>- CP-SAT solver<br>- Optimización      | `pip install ortools` |

#### **Recomendación: Enfoque Híbrido**

**Estrategia 1: Generación Aleatoria Guiada (Rápida)**

```python
# backend/app/services/generation/random_generator.py

import random
from typing import List, Set
from app.models import Feature, FeatureType

class RandomConfigurationGenerator:
    """Generador simple mediante muestreo aleatorio guiado."""

    async def generate(
        self,
        feature_model_version_id: UUID,
        count: int = 10
    ) -> List[Set[UUID]]:
        """Genera configuraciones aleatorias válidas."""
        configurations = []

        features = await self._get_features(feature_model_version_id)
        feature_tree = self._build_tree(features)

        for _ in range(count):
            selected = set()

            # Estrategia: DFS desde root, decidiendo aleatoriamente
            self._select_recursive(
                feature_tree.root,
                selected,
                feature_tree
            )

            # Validar con SAT solver
            if await self.sat_validator.is_valid(selected):
                configurations.append(selected)

        return configurations

    def _select_recursive(
        self,
        feature: Feature,
        selected: Set[UUID],
        tree
    ):
        """Selección recursiva con decisiones aleatorias."""
        # Si es MANDATORY, siempre incluir
        if feature.type == FeatureType.MANDATORY:
            selected.add(feature.id)
            for child in tree.get_children(feature.id):
                self._select_recursive(child, selected, tree)

        # Si es OPTIONAL, decidir aleatoriamente
        elif feature.type == FeatureType.OPTIONAL:
            if random.random() > 0.5:  # 50% probabilidad
                selected.add(feature.id)
                for child in tree.get_children(feature.id):
                    self._select_recursive(child, selected, tree)

        # Si es grupo OR/XOR, seleccionar según cardinalidad
        # ...
```

**Estrategia 2: Algoritmos Genéticos (Exploración Avanzada)**

```python
# backend/app/services/generation/genetic_generator.py

from deap import base, creator, tools, algorithms
import random
from typing import List, Set, Tuple

class GeneticConfigurationGenerator:
    """Generador usando algoritmos genéticos (DEAP)."""

    def __init__(self, feature_model_version_id: UUID):
        self.fm_version_id = feature_model_version_id
        self.features = None
        self.sat_validator = SATValidator()

        # Configurar DEAP
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

    async def setup(self):
        """Inicializar generador con features del modelo."""
        self.features = await self._get_features(self.fm_version_id)

        # Gen: cada bit representa si una feature está seleccionada
        self.toolbox.register(
            "attr_bool",
            random.randint,
            0, 1
        )

        # Individual: lista de bits (uno por feature)
        self.toolbox.register(
            "individual",
            tools.initRepeat,
            creator.Individual,
            self.toolbox.attr_bool,
            n=len(self.features)
        )

        # Population
        self.toolbox.register(
            "population",
            tools.initRepeat,
            list,
            self.toolbox.individual
        )

        # Operadores genéticos
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self._fitness_function)

    def _fitness_function(self, individual: List[int]) -> Tuple[float,]:
        """
        Función de fitness para evaluar configuraciones.

        Criterios:
        1. Validez lógica (SAT) - peso máximo
        2. Número de features seleccionadas - preferir más features
        3. Diversidad - explorar espacio de soluciones
        """
        # Convertir individual a set de feature IDs
        selected_ids = {
            self.features[i].id
            for i, bit in enumerate(individual)
            if bit == 1
        }

        # Validar con SAT
        is_valid = asyncio.run(
            self.sat_validator.validate_partial(selected_ids, self.fm_version_id)
        )

        if not is_valid:
            return (0.0,)  # Fitness 0 para configuraciones inválidas

        # Fitness basado en número de features
        num_selected = sum(individual)
        fitness = num_selected / len(self.features)

        return (fitness,)

    async def generate(
        self,
        population_size: int = 50,
        generations: int = 100,
        count: int = 10
    ) -> List[Set[UUID]]:
        """
        Genera configuraciones usando algoritmo genético.

        Args:
            population_size: Tamaño de población
            generations: Número de generaciones
            count: Número de configuraciones únicas a retornar
        """
        # Crear población inicial
        population = self.toolbox.population(n=population_size)

        # Evolucionar
        algorithms.eaSimple(
            population,
            self.toolbox,
            cxpb=0.7,  # Probabilidad de crossover
            mutpb=0.2,  # Probabilidad de mutación
            ngen=generations,
            verbose=False
        )

        # Extraer mejores configuraciones únicas
        valid_configs = set()
        for individual in population:
            if individual.fitness.values[0] > 0:  # Solo válidas
                config = frozenset(
                    self.features[i].id
                    for i, bit in enumerate(individual)
                    if bit == 1
                )
                valid_configs.add(config)

        # Retornar top N
        return [set(config) for config in list(valid_configs)[:count]]
```

**Estrategia 3: Constraint Programming (Google OR-Tools)**

```python
# backend/app/services/generation/cp_generator.py

from ortools.sat.python import cp_model
from typing import List, Set

class CPConfigurationGenerator:
    """Generador usando Constraint Programming (OR-Tools)."""

    async def generate_optimal(
        self,
        feature_model_version_id: UUID,
        objective: str = "maximize_features"  # o "minimize_cost"
    ) -> Set[UUID]:
        """
        Genera configuración óptima según objetivo.
        """
        features = await self._get_features(feature_model_version_id)
        constraints = await self._get_constraints(feature_model_version_id)

        # Crear modelo CP
        model = cp_model.CpModel()

        # Variables: una por feature (0 = no seleccionada, 1 = seleccionada)
        feature_vars = {}
        for f in features:
            feature_vars[str(f.id)] = model.NewBoolVar(f"feature_{f.id}")

        # Constraints de jerarquía
        for f in features:
            if f.parent_id:
                parent_var = feature_vars[str(f.parent_id)]
                child_var = feature_vars[str(f.id)]

                # child → parent
                model.Add(child_var <= parent_var)

                # Si MANDATORY: parent → child
                if f.type == FeatureType.MANDATORY:
                    model.Add(parent_var <= child_var)

        # Constraints cross-tree
        for c in constraints:
            source_var = feature_vars[str(c.source_feature_id)]
            target_var = feature_vars[str(c.target_feature_id)]

            if c.type == ConstraintType.REQUIRES:
                model.Add(source_var <= target_var)
            elif c.type == ConstraintType.EXCLUDES:
                model.Add(source_var + target_var <= 1)

        # Objetivo
        if objective == "maximize_features":
            model.Maximize(sum(feature_vars.values()))
        elif objective == "minimize_cost":
            # Asumir que features tienen costo en properties
            costs = [
                f.properties.get("cost", 1) * feature_vars[str(f.id)]
                for f in features
            ]
            model.Minimize(sum(costs))

        # Resolver
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            selected = {
                f.id
                for f in features
                if solver.Value(feature_vars[str(f.id)]) == 1
            }
            return selected

        return set()
```

---

### 3️⃣ **Analizador Estructural**

#### **Librerías Recomendadas:**

| Librería       | Uso Principal         | Ventajas                                               | Instalación                 |
| -------------- | --------------------- | ------------------------------------------------------ | --------------------------- |
| **NetworkX**   | ⭐ Análisis de grafos | - Completo<br>- Algoritmos clásicos<br>- Visualización | `pip install networkx`      |
| **graph-tool** | Grafos grandes        | - Alto rendimiento<br>- C++ backend                    | `pip install graph-tool`    |
| **igraph**     | Grafos científicos    | - Rápido<br>- Métricas avanzadas                       | `pip install python-igraph` |

#### **Recomendación Principal: NetworkX**

```python
# backend/app/services/analysis/structural_analyzer.py

import networkx as nx
from typing import List, Dict, Set, Tuple
from app.models import Feature, Constraint

class StructuralAnalyzer:
    """Analizador estructural de Feature Models usando teoría de grafos."""

    def __init__(self):
        self.graph = None
        self.feature_map = {}

    async def analyze(
        self,
        feature_model_version_id: UUID
    ) -> Dict[str, any]:
        """
        Análisis estructural completo del FM.

        Returns:
            {
                "dead_features": [...],
                "core_features": [...],
                "redundant_constraints": [...],
                "strongly_connected_components": [...],
                "metrics": {...}
            }
        """
        features = await self._get_features(feature_model_version_id)
        constraints = await self._get_constraints(feature_model_version_id)

        # Construir grafo dirigido
        self.graph = self._build_directed_graph(features, constraints)

        results = {
            "dead_features": await self._detect_dead_features(),
            "core_features": await self._detect_core_features(),
            "false_optional": await self._detect_false_optional(),
            "redundant_constraints": await self._detect_redundant_constraints(),
            "scc": self._find_strongly_connected_components(),
            "metrics": self._compute_metrics(),
            "impact_analysis": await self._compute_impact_scores(),
        }

        return results

    def _build_directed_graph(
        self,
        features: List[Feature],
        constraints: List[Constraint]
    ) -> nx.DiGraph:
        """Construye grafo dirigido del FM."""
        G = nx.DiGraph()

        # Agregar nodos (features)
        for f in features:
            self.feature_map[str(f.id)] = f
            G.add_node(
                str(f.id),
                type=f.type,
                name=f.name,
                mandatory=f.type == FeatureType.MANDATORY
            )

        # Agregar aristas (relaciones parent-child)
        for f in features:
            if f.parent_id:
                G.add_edge(
                    str(f.parent_id),
                    str(f.id),
                    relation="parent_child",
                    mandatory=f.type == FeatureType.MANDATORY
                )

        # Agregar aristas de constraints
        for c in constraints:
            G.add_edge(
                str(c.source_feature_id),
                str(c.target_feature_id),
                relation="constraint",
                type=c.type
            )

        return G

    async def _detect_dead_features(self) -> List[Dict]:
        """
        Detecta features muertas (nunca pueden ser seleccionadas).

        Método:
        1. Para cada feature, verificar con SAT si existe configuración válida que la incluya
        2. Si no existe, es dead feature
        """
        dead_features = []
        sat_validator = SATValidator()

        for feature_id in self.graph.nodes():
            # Intentar configuración forzando esta feature
            is_possible = await sat_validator.can_select_feature(
                feature_id,
                self.fm_version_id
            )

            if not is_possible:
                feature = self.feature_map[feature_id]
                dead_features.append({
                    "id": feature_id,
                    "name": feature.name,
                    "reason": "No existe configuración válida que incluya esta feature"
                })

        return dead_features

    async def _detect_core_features(self) -> List[Dict]:
        """
        Detecta features core (siempre deben estar en configuraciones válidas).

        Método:
        1. Para cada feature, verificar con SAT si existe configuración válida sin ella
        2. Si no existe, es core feature
        """
        core_features = []
        sat_validator = SATValidator()

        for feature_id in self.graph.nodes():
            # Intentar configuración excluyendo esta feature
            is_possible = await sat_validator.can_exclude_feature(
                feature_id,
                self.fm_version_id
            )

            if not is_possible:
                feature = self.feature_map[feature_id]
                core_features.append({
                    "id": feature_id,
                    "name": feature.name,
                    "reason": "Todas las configuraciones válidas deben incluirla"
                })

        return core_features

    async def _detect_false_optional(self) -> List[Dict]:
        """
        Detecta features marcadas como OPTIONAL pero que en realidad son MANDATORY.
        """
        false_optional = []

        for feature_id in self.graph.nodes():
            feature = self.feature_map[feature_id]

            if feature.type == FeatureType.OPTIONAL:
                # Verificar si en realidad es core
                is_core = await self._is_core_feature(feature_id)

                if is_core:
                    false_optional.append({
                        "id": feature_id,
                        "name": feature.name,
                        "declared_type": "OPTIONAL",
                        "actual_type": "MANDATORY",
                        "reason": "Constraints implican que siempre debe estar seleccionada"
                    })

        return false_optional

    def _find_strongly_connected_components(self) -> List[List[str]]:
        """
        Encuentra componentes fuertemente conexas (ciclos de dependencias).
        """
        sccs = list(nx.strongly_connected_components(self.graph))

        # Filtrar solo SCCs con más de un nodo (ciclos reales)
        cycles = [list(scc) for scc in sccs if len(scc) > 1]

        return cycles

    async def _detect_redundant_constraints(self) -> List[Dict]:
        """
        Detecta constraints redundantes (implícitas por otras constraints).
        """
        redundant = []
        constraints = await self._get_constraints(self.fm_version_id)

        for constraint in constraints:
            # Temporalmente remover este constraint
            is_redundant = await self._is_constraint_redundant(constraint)

            if is_redundant:
                redundant.append({
                    "constraint_id": str(constraint.id),
                    "type": constraint.type,
                    "source": str(constraint.source_feature_id),
                    "target": str(constraint.target_feature_id),
                    "reason": "Implícito por otras constraints o jerarquía"
                })

        return redundant

    def _compute_metrics(self) -> Dict[str, any]:
        """
        Calcula métricas estructurales del FM.
        """
        return {
            "total_features": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "max_depth": self._compute_max_depth(),
            "branching_factor_avg": self._compute_avg_branching_factor(),
            "density": nx.density(self.graph),
            "diameter": nx.diameter(self.graph.to_undirected()) if nx.is_connected(self.graph.to_undirected()) else None,
            "clustering_coefficient": nx.average_clustering(self.graph.to_undirected()),
        }

    async def _compute_impact_scores(self) -> Dict[str, float]:
        """
        Calcula score de impacto para cada feature.

        Impacto = cuántas otras features se ven afectadas si esta cambia.
        """
        impact_scores = {}

        for feature_id in self.graph.nodes():
            # Contar descendientes directos e indirectos
            descendants = nx.descendants(self.graph, feature_id)

            # Contar features que dependen por constraints
            dependents = [
                target
                for source, target, data in self.graph.edges(data=True)
                if source == feature_id and data.get("relation") == "constraint"
            ]

            # Score combinado
            impact_scores[feature_id] = len(descendants) + len(dependents)

        return impact_scores

    def _compute_max_depth(self) -> int:
        """Calcula profundidad máxima del árbol de features."""
        # Encontrar nodos raíz (sin padres)
        roots = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]

        max_depth = 0
        for root in roots:
            # BFS para encontrar camino más largo
            depths = nx.single_source_shortest_path_length(self.graph, root)
            max_depth = max(max_depth, max(depths.values()) if depths else 0)

        return max_depth

    def _compute_avg_branching_factor(self) -> float:
        """Calcula factor de ramificación promedio."""
        out_degrees = [d for n, d in self.graph.out_degree() if d > 0]
        return sum(out_degrees) / len(out_degrees) if out_degrees else 0
```

---

## 🎨 Patrón de Integración: Strategy Pattern

Para integrar los 3 componentes de manera flexible, recomiendo usar **Strategy Pattern**:

```python
# backend/app/services/validation/validator_strategy.py

from abc import ABC, abstractmethod
from typing import Protocol, List, Tuple
from enum import Enum

class ValidationStrategy(str, Enum):
    SAT = "sat"  # SAT solver (exacto)
    SMT = "smt"  # SMT solver (con teorías)
    HEURISTIC = "heuristic"  # Validación heurística rápida

class IValidator(Protocol):
    """Interfaz para validadores."""

    async def validate_configuration(
        self,
        configuration: Configuration,
        fm_version_id: UUID
    ) -> Tuple[bool, List[str]]:
        """Valida configuración."""
        ...

class ValidatorFactory:
    """Factory para crear validadores según estrategia."""

    @staticmethod
    def create(strategy: ValidationStrategy) -> IValidator:
        if strategy == ValidationStrategy.SAT:
            return SATValidator()
        elif strategy == ValidationStrategy.SMT:
            return SMTValidator()
        elif strategy == ValidationStrategy.HEURISTIC:
            return HeuristicValidator()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

# Uso en endpoints
@router.post("/validate/")
async def validate_configuration(
    config: Configuration,
    strategy: ValidationStrategy = ValidationStrategy.SAT
):
    validator = ValidatorFactory.create(strategy)
    is_valid, errors = await validator.validate_configuration(config)

    return {
        "valid": is_valid,
        "errors": errors,
        "strategy_used": strategy
    }
```

---

## 📦 Dependencias a Agregar

```toml
# backend/pyproject.toml

[project]
dependencies = [
    # ... existentes ...

    # Motor de Validación
    "python-sat>=0.1.8.dev13",  # SAT solving
    "z3-solver>=4.12.2.0",       # SMT solving
    "networkx>=3.2",             # Análisis de grafos
    "deap>=1.4.1",               # Algoritmos genéticos
    "ortools>=9.8.3296",         # Constraint Programming

    # Opcional: Visualización
    "matplotlib>=3.8.0",         # Para visualizar grafos
    "graphviz>=0.20.1",          # Para exportar grafos
]
```

---

## 🚀 LLM / LangChain - ¿Cuándo Usarlo?

### **Recomendación: NO usar LLM para validación formal**

**Razones:**

1. ❌ **No determinístico**: LLMs no garantizan corrección formal
2. ❌ **Lento**: Latencia de inferencia vs. microsegundos del SAT solver
3. ❌ **Costoso**: Tokens vs. computación local gratuita
4. ❌ **No explicable**: Difícil debugging de decisiones

### **SÍ usar LLM para:**

#### 1. **Asistencia al Usuario (UX)**

```python
# backend/app/services/ai/feature_assistant.py

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class FeatureModelAssistant:
    """Asistente LLM para ayudar a usuarios a entender FMs."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")

    async def explain_constraint(
        self,
        constraint: Constraint,
        context: str
    ) -> str:
        """Explica en lenguaje natural por qué existe un constraint."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en Feature Models educativos."),
            ("user",
             f"Explica en español por qué esta restricción existe:\n"
             f"Tipo: {constraint.type}\n"
             f"Desde: {constraint.source_feature.name}\n"
             f"Hacia: {constraint.target_feature.name}\n"
             f"Contexto: {context}")
        ])

        response = await self.llm.ainvoke(prompt.format_messages())
        return response.content

    async def suggest_features(
        self,
        partial_config: Set[UUID],
        fm_version_id: UUID
    ) -> List[str]:
        """Sugiere features complementarias usando LLM."""
        selected_names = [f.name for f in await self._get_features_by_ids(partial_config)]

        prompt = f"""
        El estudiante ha seleccionado: {', '.join(selected_names)}

        Basándote en un plan de estudios de ingeniería, ¿qué otras materias
        complementarias recomendarías y por qué?
        """

        response = await self.llm.ainvoke(prompt)
        return self._parse_suggestions(response.content)
```

#### 2. **Generación de Explicaciones de Errores**

```python
async def explain_validation_error(
    self,
    error_type: str,
    conflicting_features: List[str]
) -> str:
    """Traduce errores técnicos a lenguaje comprensible."""
    prompt = f"""
    Un estudiante intentó seleccionar: {', '.join(conflicting_features)}

    Error técnico: {error_type}

    Explica en términos pedagógicos simples por qué esta combinación no es válida.
    """

    response = await self.llm.ainvoke(prompt)
    return response.content
```

#### 3. **Generación de Descripciones Automáticas**

```python
async def generate_feature_description(
    self,
    feature_name: str,
    context: Dict
) -> str:
    """Genera descripción pedagógica de una feature."""
    # Útil para features creadas automáticamente
```

### **Arquitectura Híbrida Recomendada:**

```
┌────────────────────────────────────────┐
│         USER REQUEST                   │
│  "¿Por qué no puedo seleccionar X?"   │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│     1. SAT VALIDATOR (Formal)         │
│  Determina: "Constraint violation"    │
│  Identifica: features conflictivas    │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│     2. LLM EXPLAINER (Natural)        │
│  Traduce: error técnico → lenguaje    │
│  natural comprensible                 │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│         USER RESPONSE                  │
│  "No puedes tomar Cálculo 2 porque    │
│   no has aprobado Cálculo 1"          │
└────────────────────────────────────────┘
```

---

## 📊 Resumen Ejecutivo

### **Patrón Arquitectónico:**

✅ **Layered Architecture (Clean/Hexagonal variant)**

- Clara separación de responsabilidades
- Dependency Injection
- Ports & Adapters

### **Motor de Validación:**

| Componente           | Librería Principal | Alternativas       | Complejidad |
| -------------------- | ------------------ | ------------------ | ----------- |
| **Validador Lógico** | python-sat         | z3-solver, pycosat | Media       |
| **Generador**        | DEAP + OR-Tools    | scipy.optimize     | Alta        |
| **Analizador**       | NetworkX           | igraph, graph-tool | Baja-Media  |

### **Estrategia de Implementación:**

```
Fase 1 (2-3 semanas):
├── Validador SAT básico (python-sat)
├── Generador aleatorio guiado
└── Analizador NetworkX (dead features, core features)

Fase 2 (3-4 semanas):
├── Validador SMT (z3-solver)
├── Generador genético (DEAP)
└── Analizador avanzado (métricas, impacto)

Fase 3 (2-3 semanas):
├── Generador CP (OR-Tools)
├── Optimización de performance
└── LLM Assistant (explicaciones)
```

### **NO usar LLM para:**

❌ Validación formal (usar SAT/SMT)
❌ Generación de configuraciones (usar algoritmos exactos)
❌ Análisis estructural (usar grafos)

### **SÍ usar LLM para:**

✅ Explicaciones en lenguaje natural
✅ Asistencia pedagógica
✅ Generación de descripciones\begin{figure}[H]
            \centering
            \resizebox{\textwidth}{!}{%
                \begin{forest}
                    for tree={
                        draw,
                        rounded corners,
                        font=\footnotesize,
                        node options={align=center},
                        anchor=north,
                        parent anchor=south,
                        l sep=15pt,
                        s sep=15pt,
                        edge={-latex},
                        grow=0,
                        child anchor=west,
                        parent anchor=east
                    }
                    [Estructura de Datos I
                        [Fundamentos y Análisis]
                        [Estructuras Lineales
                            [Arreglos]
                            [Listas Enlazadas]
                            [Listas Circulares (Opc.)]
                        ]
                        [Pilas
                            [Implementación (XOR)
                                [Con Arreglos]
                                [Con Listas]
                            ]
                        ]
                        [Colas
                            [FIFO]
                            [Prioridad]
                            [Deque (Opc.)]
                        ]
                        [Árboles Binarios]
                        [Algoritmos Ordenamiento]
                    ]
                    \end{forest}%
            }
            \caption{Representación simplificada del \ac{FM} de la asignatura Estructura de Datos I.}
            \label{fig:fm_data_structures}
            \end{figure}
✅ Traducción de errores técnicos

---

**Documento generado:** 9 de diciembre de 2025  
**Versión:** 1.0  
**Integración con:** SPL_TECHNIQUES_ANALYSIS.md
