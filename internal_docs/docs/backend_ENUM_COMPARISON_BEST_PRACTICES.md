# Mejores Prácticas para Comparación de Enums

## ⚠️ Problema Común

Comparar valores de enums usando `.value` puede llevar a errores difíciles de detectar si los valores internos cambian o si hay errores tipográficos en los strings.

## ❌ Forma INCORRECTA (Propensa a errores)

```python
# MAL: Comparando con strings directamente
if feature.type.value == "MANDATORY":
    ...

if group.group_type.value == "XOR":
    ...

if relation.type.value == "requires":
    ...
```

**Problemas:**

- ❌ No hay verificación de tipos en tiempo de compilación
- ❌ Los errores tipográficos no se detectan hasta runtime
- ❌ Si cambia el valor interno del enum, el código se rompe silenciosamente
- ❌ El IDE no puede autocompletar ni refactorizar correctamente

## ✅ Forma CORRECTA (Segura y mantenible)

```python
from app.enums import FeatureType, FeatureGroupType, FeatureRelationType

# BIEN: Comparando directamente contra el enum
if feature.type == FeatureType.MANDATORY:
    ...

if group.group_type == FeatureGroupType.ALTERNATIVE:
    ...

if relation.type == FeatureRelationType.REQUIRED:
    ...
```

**Beneficios:**

- ✅ Verificación de tipos en tiempo de compilación
- ✅ Errores tipográficos detectados inmediatamente
- ✅ Refactorización segura con IDE
- ✅ Autocompletado funciona correctamente
- ✅ El código es más legible y mantenible

## 📋 Enums Disponibles en el Proyecto

### `FeatureType` (app.enums)

```python
class FeatureType(str, Enum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
```

**Uso correcto:**

```python
if feature.type == FeatureType.MANDATORY:
    print("Esta feature es obligatoria")
```

### `FeatureGroupType` (app.enums)

```python
class FeatureGroupType(str, Enum):
    ALTERNATIVE = "alternative"  # XOR - elegir exactamente una
    OR = "or"                     # OR - elegir una o más
```

**Uso correcto:**

```python
if group.group_type == FeatureGroupType.ALTERNATIVE:
    print("Grupo XOR: elige exactamente una opción")
elif group.group_type == FeatureGroupType.OR:
    print("Grupo OR: elige una o más opciones")
```

### `FeatureRelationType` (app.enums)

```python
class FeatureRelationType(str, Enum):
    REQUIRED = "requires"   # Una feature requiere otra
    EXCLUDES = "excludes"   # Una feature excluye otra
```

**Uso correcto:**

```python
if relation.type == FeatureRelationType.REQUIRED:
    print(f"{source} requiere {target}")
elif relation.type == FeatureRelationType.EXCLUDES:
    print(f"{source} excluye {target}")
```

### `ModelStatus` (app.enums)

```python
class ModelStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
```

**Uso correcto:**

```python
if version.status == ModelStatus.PUBLISHED:
    print("Versión publicada y lista para producción")
```

## 🔧 Archivos Corregidos

Los siguientes archivos ya han sido actualizados para seguir estas mejores prácticas:

1. **`app/repositories/a_sync/feature_model_version.py`**

   - ✅ `get_statistics()`: Comparaciones de FeatureType, FeatureGroupType, FeatureRelationType

2. **`app/services/feature_model_tree_builder.py`**

   - ✅ `_generate_group_description()`: FeatureGroupType.ALTERNATIVE y OR
   - ✅ `_build_relations()`: FeatureRelationType.REQUIRED y EXCLUDES
   - ✅ `_calculate_statistics()`: FeatureType, FeatureGroupType, FeatureRelationType

3. **`app/api/v1/endpoints/feature_model_statistics.py`**
   - ✅ `get_latest_feature_model_statistics()`: ModelStatus.PUBLISHED

## 📝 Checklist para Code Review

Al revisar código que trabaja con enums, verificar:

- [ ] Se importan los enums necesarios al inicio del archivo
- [ ] Las comparaciones usan el enum directamente (no `.value`)
- [ ] No hay strings mágicos en lugar de valores de enum
- [ ] Los casos switch/if-elif cubren todos los valores del enum
- [ ] Se usa el enum correcto (no confundir ALTERNATIVE con XOR)

## 🚀 Ejemplo Completo

```python
from app.enums import FeatureType, FeatureGroupType, FeatureRelationType, ModelStatus

def process_feature_model(version: FeatureModelVersion) -> dict:
    """Ejemplo de uso correcto de enums."""

    # Estado del modelo
    if version.status == ModelStatus.DRAFT:
        print("⚠️ Aún en borrador")
    elif version.status == ModelStatus.PUBLISHED:
        print("✅ Versión publicada")

    # Tipos de features
    for feature in version.features:
        if feature.type == FeatureType.MANDATORY:
            print(f"📌 {feature.name} es obligatoria")
        elif feature.type == FeatureType.OPTIONAL:
            print(f"⭕ {feature.name} es opcional")

    # Tipos de grupos
    for group in version.feature_groups:
        if group.group_type == FeatureGroupType.ALTERNATIVE:
            print(f"🔀 Grupo XOR: elige UNA opción")
        elif group.group_type == FeatureGroupType.OR:
            print(f"🔗 Grupo OR: elige una o MÁS opciones")

    # Tipos de relaciones
    for relation in version.feature_relations:
        source = relation.source_feature.name
        target = relation.target_feature.name

        if relation.type == FeatureRelationType.REQUIRED:
            print(f"➡️ {source} requiere {target}")
        elif relation.type == FeatureRelationType.EXCLUDES:
            print(f"⛔ {source} excluye {target}")

    return {
        "status": version.status,  # Ya es un enum, no necesita .value
        "features": len(version.features),
        "groups": len(version.feature_groups),
    }
```

## 🎯 Regla de Oro

> **Siempre compara enums con enums, nunca con strings.**

Si necesitas el valor string para serialización, úsalo **solo al final**:

```python
# ✅ Comparación correcta
if feature.type == FeatureType.MANDATORY:
    # ✅ Obtener valor para JSON solo cuando sea necesario
    feature_dict = {
        "type": feature.type.value,  # Aquí sí está bien usar .value
        "name": feature.name
    }
```

---

**Fecha de actualización:** 10 de diciembre de 2025  
**Archivos revisados:** 3 archivos principales actualizados
