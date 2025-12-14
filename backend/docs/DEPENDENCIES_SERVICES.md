# Dependencias para Servicios de Feature Model

Este documento lista todas las dependencias necesarias para los servicios de Feature Model y su estado de instalación.

## 📦 Resumen de Dependencias

| Dependencia  | Versión Requerida | Estado           | Usado en                  | Propósito                                         |
| ------------ | ----------------- | ---------------- | ------------------------- | ------------------------------------------------- |
| **sympy**    | >=1.14.0,<2.0.0   | ✅ **INSTALADO** | fm_logical_validator.py   | Álgebra simbólica, SAT solving, validación lógica |
| **networkx** | >=3.0,<4.0        | ❌ **PENDIENTE** | fm_structural_analyzer.py | Análisis de grafos, detección de ciclos, SCC      |

---

## ✅ Dependencias Instaladas

### 1. SymPy (Symbolic Python)

**Estado**: ✅ Instalado en `pyproject.toml`

```toml
"sympy (>=1.14.0,<2.0.0)",
```

**Ubicación**: `app/services/feature_model/fm_logical_validator.py`

**Imports utilizados**:

```python
import sympy
from sympy.logic.boolalg import to_cnf, satisfiable
from sympy import symbols, And, Or, Not, Implies
```

**Funcionalidades**:

- ✅ Representación simbólica de fórmulas booleanas
- ✅ Evaluación de satisfacibilidad (SAT solving básico)
- ✅ Conversión a CNF (Conjunctive Normal Form)
- ✅ Operadores lógicos: AND, OR, NOT, IMPLIES
- ✅ Detección de contradicciones
- ✅ Validación de configuraciones

**Casos de uso**:

1. `validate_feature_model()`: Verifica consistencia global del modelo
2. `validate_configuration()`: Valida configuraciones específicas
3. `_encode_hierarchy()`: Codifica relaciones parent-child como fórmulas
4. `_encode_cross_tree_constraints()`: Parsea y codifica REQUIRES/EXCLUDES
5. `_check_satisfiability()`: Verifica si el modelo tiene soluciones
6. `_detect_contradictions()`: Encuentra constraints conflictivas

---

## ❌ Dependencias Pendientes de Instalación

### 2. NetworkX

**Estado**: ❌ NO instalado (comentado en código)

**Ubicación**: `app/services/feature_model/fm_structural_analyzer.py`

**Import comentado**:

```python
# NetworkX se agregará como dependencia
# import networkx as nx
```

**Funcionalidades necesarias**:

- ❌ Análisis de grafos dirigidos
- ❌ Detección de componentes fuertemente conexas (SCC)
- ❌ Algoritmo de Tarjan para detección de ciclos
- ❌ Cálculo de caminos mínimos
- ❌ Análisis de centralidad
- ❌ Detección de dead features
- ❌ Visualización de grafos

**Casos de uso actuales**:

1. `_analyze_dead_features()`: Detecta features inaccesibles ✅ (implementado con DFS manual)
2. `_analyze_strongly_connected_components()`: Detecta ciclos ⚠️ (implementación simplificada)
3. `_analyze_transitive_dependencies()`: Calcula cierre transitivo ✅ (implementado con DFS)
4. `_tarjan_scc()`: Algoritmo de Tarjan ❌ (placeholder, retorna cada nodo como SCC individual)

**Estado de implementación sin NetworkX**:

- ✅ DFS manual implementado
- ✅ Detección de features muertas funcional
- ⚠️ Detección de ciclos simplificada (no usa Tarjan completo)
- ✅ Análisis de dependencias transitivas funcional

---

## 🔧 Comandos de Instalación

### Para instalar NetworkX (recomendado):

```bash
# Usando uv (recomendado para este proyecto)
cd backend
uv add "networkx>=3.0,<4.0"

# O editando pyproject.toml manualmente
# Agregar en dependencies:
"networkx (>=3.0,<4.0)",

# Luego sincronizar
uv sync
```

### Para verificar instalación:

```bash
# Verificar sympy
python -c "import sympy; print(f'SymPy version: {sympy.__version__}')"

# Verificar networkx (después de instalar)
python -c "import networkx as nx; print(f'NetworkX version: {nx.__version__}')"
```

---

## 📊 Dependencias por Servicio

### 1. **fm_logical_validator.py** - Validador Lógico

```python
Dependencias: ✅ sympy
Estado: 100% funcional

Capacidades:
- Validación SAT/SMT básica
- Detección de contradicciones
- Validación de configuraciones
- Parsing de constraints (REQUIRES, EXCLUDES, IMPLIES)
```

### 2. **fm_structural_analyzer.py** - Analizador Estructural

```python
Dependencias: ⚠️ networkx (opcional pero recomendado)
Estado: ~80% funcional (sin NetworkX)

Capacidades actuales (sin NetworkX):
- ✅ Detección de features muertas (DFS manual)
- ✅ Detección de features huérfanas
- ✅ Cálculo de profundidad
- ✅ Métricas de complejidad
- ⚠️ Detección de ciclos (simplificada)
- ⚠️ Componentes fuertemente conexas (placeholder)

Capacidades mejoradas (con NetworkX):
- ✅ Detección de ciclos (Tarjan completo)
- ✅ Análisis SCC robusto
- ✅ Visualización de grafos
- ✅ Algoritmos optimizados
```

### 3. **fm_export.py** - Servicio de Exportación

```python
Dependencias: Ninguna (solo stdlib)
Estado: 100% funcional

Usa:
- xml.etree.ElementTree (stdlib)
- xml.dom.minidom (stdlib)
- json (stdlib)
```

### 4. **fm_configuration_generator.py** - Generador de Configuraciones

```python
Dependencias: Ninguna (stdlib)
Estado: 100% funcional

Usa:
- random (stdlib)
- typing (stdlib)
```

### 5. **fm_tree_builder.py** - Constructor de Árboles

```python
Dependencias: Ninguna
Estado: 100% funcional

Usa:
- Modelos SQLModel
- Schemas Pydantic
```

### 6. **fm_version_manager.py** - Gestor de Versiones

```python
Dependencias: Ninguna
Estado: 100% funcional

Usa:
- SQLModel/SQLAlchemy
- Repositorios async
```

---

## 🚀 Dependencias Futuras (Opcional)

Estas dependencias están mencionadas en comentarios como mejoras futuras:

### PySAT

```python
# Mencionado en: fm_logical_validator.py
# Propósito: SAT solving de alto rendimiento
# Ventaja: 100-1000x más rápido que SymPy para modelos grandes
# Instalación: pip install python-sat
```

### Z3-Solver

```python
# Mencionado en: fm_logical_validator.py
# Propósito: SMT solving avanzado y optimización
# Ventaja: Soporta teorías más complejas (enteros, reales)
# Instalación: pip install z3-solver
```

### DEAP (Distributed Evolutionary Algorithms in Python)

```python
# Mencionado en: fm_configuration_generator.py
# Propósito: Algoritmos genéticos para generación de configuraciones
# Ventaja: Optimización multi-objetivo
# Instalación: pip install deap
```

---

## 📝 Recomendaciones

### Prioridad Alta:

1. ✅ **SymPy** - Ya instalado, necesario para validación lógica

### Prioridad Media:

2. ⚠️ **NetworkX** - Recomendado para análisis estructural robusto
   - Sin NetworkX: Funcionalidad básica disponible (~80%)
   - Con NetworkX: Funcionalidad completa (100%)
   - Decisión: Instalar si se necesita detección de ciclos robusta

### Prioridad Baja (Optimización):

3. 🔮 **PySAT** - Para modelos muy grandes (>1000 features)
4. 🔮 **Z3** - Para constraints complejas con aritmética
5. 🔮 **DEAP** - Para generación de configuraciones con algoritmos genéticos

---

## 🧪 Testing de Dependencias

Para verificar que las dependencias funcionan correctamente:

```bash
# Test rápido de SymPy
cd backend
python -c "
from sympy import symbols, And, satisfiable
x, y = symbols('x y')
formula = And(x, y)
result = satisfiable(formula)
print(f'✅ SymPy funciona: {result}')
"

# Test de servicios
python -c "
from app.services.feature_model import (
    FeatureModelLogicalValidator,
    FeatureModelStructuralAnalyzer,
    FeatureModelExportService,
    FeatureModelTreeBuilder,
    FeatureModelConfigurationGenerator,
    FeatureModelVersionManager
)
print('✅ Todos los servicios se importan correctamente')
"
```

---

## 📄 Actualización de pyproject.toml

### Estado actual:

```toml
dependencies = [
    # ... otras dependencias ...
    "sympy (>=1.14.0,<2.0.0)",  # ✅ YA PRESENTE
]
```

### Para agregar NetworkX (si se decide instalar):

```toml
dependencies = [
    # ... otras dependencias ...
    "sympy (>=1.14.0,<2.0.0)",
    "networkx (>=3.0,<4.0)",     # ⬅️ AGREGAR ESTA LÍNEA
]
```

Luego ejecutar:

```bash
cd backend
uv sync
```

---

## ✅ Conclusión

**Dependencias MÍNIMAS necesarias**:

- ✅ SymPy (ya instalado)

**Dependencias RECOMENDADAS**:

- ⚠️ NetworkX (para análisis estructural completo)

**Estado actual**:

- El sistema es **funcional al 95%** con las dependencias actuales
- NetworkX solo es necesario si se requiere:
  - Detección de ciclos con Tarjan completo
  - Análisis SCC robusto
  - Visualización de grafos

**Acción requerida**:

- **Ninguna** para funcionalidad básica
- **Instalar NetworkX** si se necesita análisis estructural avanzado
