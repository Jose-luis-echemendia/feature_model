# Documentación de Excepciones - Feature Models API

## 📚 Guía de Excepciones Personalizadas

Este documento describe todas las excepciones personalizadas del dominio de Feature Models, sus códigos HTTP, mensajes y cuándo se lanzan.

---

## 🔴 Excepciones Base (HTTP Status Codes)

### `NotFoundException` (404)

**Uso:** Recurso no encontrado

```python
raise NotFoundException(detail="Resource not found")
```

### `BusinessLogicException` (400)

**Uso:** Error de lógica de negocio

```python
raise BusinessLogicException(detail="Invalid business operation")
```

### `UnprocessableEntityException` (422)

**Uso:** Entidad con errores de validación

```python
raise UnprocessableEntityException(detail="Invalid entity structure")
```

### `ConflictException` (409)

**Uso:** Conflicto con estado actual del recurso

```python
raise ConflictException(detail="Resource already exists")
```

### `ForbiddenException` (403)

**Uso:** Acceso prohibido

```python
raise ForbiddenException(detail="Insufficient permissions")
```

### `UnauthorizedException` (401)

**Uso:** No autenticado

```python
raise UnauthorizedException(detail="Authentication required")
```

---

## 🏗️ Feature Model - Excepciones de Entidades (404)

### `FeatureModelNotFoundException`

**Cuándo:** Feature Model solicitado no existe

```python
raise FeatureModelNotFoundException(model_id="uuid-here")
```

**Mensaje:** `"Feature Model with ID 'uuid-here' not found"`

### `FeatureModelVersionNotFoundException`

**Cuándo:** Versión del Feature Model no existe

```python
# Con ID
raise FeatureModelVersionNotFoundException(version_id="uuid-here")
# Con número de versión
raise FeatureModelVersionNotFoundException(version_number=5)
```

**Mensajes:**

- `"Feature Model version 'uuid-here' not found"`
- `"Feature Model version 5 not found"`

### `FeatureNotFoundException`

**Cuándo:** Feature solicitada no existe

```python
raise FeatureNotFoundException(feature_id="uuid-here")
```

**Mensaje:** `"Feature with ID 'uuid-here' not found"`

---

## 📦 Version Management - Excepciones de Versionado (400/409/404)

### `InvalidVersionStateException` (400)

**Cuándo:** Versión no está en estado correcto para la operación

```python
raise InvalidVersionStateException(
    current_state="PUBLISHED",
    required_state="DRAFT",
    operation="modify version"
)
```

**Mensaje:** `"Cannot modify version: version is in state 'PUBLISHED', but 'DRAFT' is required"`

**Transiciones de estado válidas:**

- `DRAFT` → `PUBLISHED` (publicar)
- `PUBLISHED` → `ARCHIVED` (archivar)
- `ARCHIVED` → `PUBLISHED` (restaurar)

### `VersionAlreadyPublishedException` (409)

**Cuándo:** Intento de modificar versión publicada (inmutable)

```python
raise VersionAlreadyPublishedException(version_id="uuid-here")
```

**Mensaje:** `"Version 'uuid-here' is already published and cannot be modified. Published versions are immutable."`

### `NoPublishedVersionException` (404)

**Cuándo:** No existe versión publicada del Feature Model

```python
raise NoPublishedVersionException(model_id="uuid-here")
```

**Mensaje:** `"Feature Model 'uuid-here' has no published versions"`

---

## 🌳 Structural Validation - Validación de Estructura (422)

### `InvalidTreeStructureException`

**Cuándo:** Estructura del árbol de features inválida

```python
raise InvalidTreeStructureException(reason="Circular reference detected")
```

**Mensaje:** `"Invalid tree structure: Circular reference detected"`

### `MissingRootFeatureException`

**Cuándo:** Feature Model sin feature raíz

```python
raise MissingRootFeatureException()
```

**Mensaje:** `"Feature Model must have exactly one root feature (feature without parent)"`

### `MultipleRootFeaturesException`

**Cuándo:** Feature Model con múltiples features raíz

```python
raise MultipleRootFeaturesException(count=3)
```

**Mensaje:** `"Feature Model must have exactly one root feature, but found 3"`

### `CyclicDependencyException`

**Cuándo:** Ciclo detectado en árbol o relaciones

```python
raise CyclicDependencyException(cycle_description="A → B → C → A")
```

**Mensaje:** `"Cyclic dependency detected in feature tree: A → B → C → A"`

### `OrphanFeatureException`

**Cuándo:** Feature sin parent que no es raíz

```python
raise OrphanFeatureException(feature_id="uuid-here")
```

**Mensaje:** `"Feature 'uuid-here' is orphaned (no parent and not root)"`

---

## 🔗 Relationship Validation - Validación de Relaciones (422/409)

### `InvalidRelationException` (422)

**Cuándo:** Relación entre features inválida

```python
raise InvalidRelationException(reason="Source and target cannot be the same")
```

**Mensaje:** `"Invalid feature relation: Source and target cannot be the same"`

### `SelfRelationException` (422)

**Cuándo:** Feature con relación consigo misma

```python
raise SelfRelationException(feature_id="uuid-here")
```

**Mensaje:** `"Feature 'uuid-here' cannot have a relation with itself"`

### `DuplicateRelationException` (409)

**Cuándo:** Relación duplicada entre features

```python
raise DuplicateRelationException(source_id="uuid-1", target_id="uuid-2")
```

**Mensaje:** `"Relation between 'uuid-1' and 'uuid-2' already exists"`

### `ConflictingRelationsException` (422)

**Cuándo:** Relaciones conflictivas (requires y excludes simultáneas)

```python
raise ConflictingRelationsException(feature1="Feature1", feature2="Feature2")
```

**Mensaje:** `"Conflicting relations between 'Feature1' and 'Feature2'. Features cannot both require and exclude each other."`

---

## 👥 Group Validation - Validación de Grupos (422)

### `InvalidGroupCardinalityException`

**Cuándo:** Cardinalidades de grupo inválidas

```python
raise InvalidGroupCardinalityException(min_card=2, max_card=5, children_count=1)
```

**Mensaje:** `"Invalid group cardinality: min=2, max=5, but group has 1 children. Must satisfy: 0 <= min <= max <= children_count"`

**Regla:** `0 ≤ min ≤ max ≤ número_de_hijos`

### `EmptyGroupException`

**Cuándo:** Grupo sin features hijas

```python
raise EmptyGroupException(group_id="uuid-here")
```

**Mensaje:** `"Group 'uuid-here' must have at least one child feature"`

### `InvalidAlternativeGroupException`

**Cuándo:** Grupo alternative (XOR) con configuración inválida

```python
raise InvalidAlternativeGroupException(reason="Must have at least 2 children")
```

**Mensaje:** `"Invalid alternative group: Must have at least 2 children"`

**Regla Alternative (XOR):** Exactamente 1 feature seleccionada del grupo

### `InvalidOrGroupException`

**Cuándo:** Grupo OR con configuración inválida

```python
raise InvalidOrGroupException(reason="Max cardinality cannot be less than min")
```

**Mensaje:** `"Invalid OR group: Max cardinality cannot be less than min"`

**Regla OR:** Al menos 1 feature seleccionada del grupo

---

## ⚠️ Constraint Validation - Validación de Constraints (422)

### `InvalidConstraintException`

**Cuándo:** Constraint con expresión inválida

```python
raise InvalidConstraintException(
    expression="Feature1 AND AND Feature2",
    reason="Syntax error: duplicate operator"
)
```

**Mensaje:** `"Invalid constraint expression: 'Feature1 AND AND Feature2'. Reason: Syntax error: duplicate operator"`

### `UnsatisfiableConstraintException`

**Cuándo:** Constraint hace el modelo insatisfacible

```python
raise UnsatisfiableConstraintException(constraint_name="Constraint1")
```

**Mensaje:** `"Constraint 'Constraint1' makes the model unsatisfiable. No valid configuration can satisfy all constraints."`

### `ConflictingConstraintsException`

**Cuándo:** Constraints conflictivos entre sí

```python
raise ConflictingConstraintsException(
    constraint1="Feature1 => Feature2",
    constraint2="Feature1 => !Feature2"
)
```

**Mensaje:** `"Conflicting constraints: 'Feature1 => Feature2' and 'Feature1 => !Feature2' cannot be satisfied simultaneously"`

---

## ✅ Configuration Validation - Validación de Configuraciones (422)

### `InvalidConfigurationException`

**Cuándo:** Configuración viola restricciones del modelo

```python
raise InvalidConfigurationException(reason="Violates constraint C1")
```

**Mensaje:** `"Invalid configuration: Violates constraint C1"`

### `MandatoryFeatureMissingException`

**Cuándo:** Feature mandatory no seleccionada

```python
raise MandatoryFeatureMissingException(feature_name="CoreFeature")
```

**Mensaje:** `"Mandatory feature 'CoreFeature' must be selected in configuration"`

### `ExcludedFeaturesSelectedException`

**Cuándo:** Features con relación 'excludes' seleccionadas juntas

```python
raise ExcludedFeaturesSelectedException(feature1="FeatureA", feature2="FeatureB")
```

**Mensaje:** `"Features 'FeatureA' and 'FeatureB' exclude each other and cannot be selected together"`

### `RequiredFeatureMissingException`

**Cuándo:** Feature requerida no seleccionada

```python
raise RequiredFeatureMissingException(
    source_feature="FeatureA",
    required_feature="FeatureB"
)
```

**Mensaje:** `"Feature 'FeatureA' requires 'FeatureB' to be selected"`

### `GroupCardinalityViolationException`

**Cuándo:** Selección no cumple cardinalidad del grupo

```python
raise GroupCardinalityViolationException(
    group_name="ColorGroup",
    selected=3,
    min_card=1,
    max_card=2
)
```

**Mensaje:** `"Group 'ColorGroup' requires between 1 and 2 features to be selected, but 3 were selected"`

---

## 📤 Export - Excepciones de Exportación (400)

### `UnsupportedExportFormatException`

**Cuándo:** Formato de exportación no soportado

```python
raise UnsupportedExportFormatException(format="UNKNOWN_FORMAT")
```

**Mensaje:** `"Export format 'UNKNOWN_FORMAT' is not supported. Supported formats: XML, SPLOT_XML, TVL, DIMACS, JSON, UVL, DOT, MERMAID"`

**Formatos soportados:**

- `XML` - FeatureIDE XML
- `SPLOT_XML` - SPLOT XML
- `TVL` - Textual Variability Language
- `DIMACS` - CNF format para SAT solvers
- `JSON` - JSON simplificado
- `UVL` - Universal Variability Language
- `DOT` - Graphviz
- `MERMAID` - Mermaid diagrams

### `ExportFailedException`

**Cuándo:** Error durante exportación

```python
raise ExportFailedException(format="XML", reason="Missing root element")
```

**Mensaje:** `"Failed to export to XML: Missing root element"`

---

## 🔍 Analysis - Excepciones de Análisis (400)

### `DeadFeatureDetectedException`

**Cuándo:** Features muertas detectadas (nunca seleccionables)

```python
raise DeadFeatureDetectedException(
    feature_names=["Feature1", "Feature2", "Feature3"]
)
```

**Mensaje:** `"Dead features detected: 'Feature1', 'Feature2', 'Feature3'. These features can never be selected in any valid configuration."`

### `FalseOptionalDetectedException`

**Cuándo:** False optional features detectadas (siempre seleccionadas)

```python
raise FalseOptionalDetectedException(
    feature_names=["OptionalFeature1", "OptionalFeature2"]
)
```

**Mensaje:** `"False optional features detected: 'OptionalFeature1', 'OptionalFeature2'. These features appear optional but are always selected."`

---

## 🎯 Mejores Prácticas de Uso

### 1. **Usar excepciones específicas** en lugar de genéricas

```python
# ❌ Evitar
raise HTTPException(status_code=404, detail="Not found")

# ✅ Preferir
raise FeatureModelNotFoundException(model_id=model_id)
```

### 2. **Proporcionar contexto en los mensajes**

```python
# ❌ Evitar
raise InvalidRelationException(reason="Invalid")

# ✅ Preferir
raise InvalidRelationException(
    reason=f"Source feature '{source_id}' does not exist in version"
)
```

### 3. **Capturar y re-lanzar con excepciones de dominio**

```python
try:
    # operación que puede fallar
    process_configuration()
except ValueError as e:
    raise InvalidConfigurationException(reason=str(e))
```

### 4. **Documentar excepciones en endpoints**

```python
@router.get(
    "/feature-models/{model_id}",
    responses={
        404: {
            "description": "Feature Model not found",
            "model": ErrorResponse
        },
        403: {
            "description": "Insufficient permissions",
            "model": ErrorResponse
        }
    }
)
async def get_feature_model(model_id: UUID):
    """..."""
```

---

## 📖 Ejemplo de Respuesta de Error

Todas las excepciones generan una respuesta con el siguiente formato:

```json
{
  "object": "feature-model.get",
  "code": 404,
  "status": "error",
  "message": {
    "http_code": 404,
    "error_code": 1005,
    "category": "http_error",
    "description": "Feature Model with ID 'abc-123' not found",
    "request_id": "7e435a39-8a83-4682-93c0-0f6c17a900ac"
  }
}
```

---

## 🧪 Testing de Excepciones

Ver tests completos en: `app/tests/exceptions/test_feature_model_exceptions.py`

```python
def test_feature_model_not_found():
    exc = FeatureModelNotFoundException(model_id="test-id")
    assert exc.status_code == 404
    assert "test-id" in str(exc.detail)
```

---

## 🔄 Actualización y Mantenimiento

- **Versión:** 1.0.0
- **Última actualización:** Diciembre 2025
- **Mantenedor:** Backend Team
- **Archivo fuente:** `app/exceptions/feature_model_exceptions.py`
