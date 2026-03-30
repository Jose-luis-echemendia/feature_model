# 🧩 UVL para Feature Models

## 📌 Objetivo

Este documento describe el flujo de trabajo UVL (Universal Variability Language) para **edición paralela** texto/estructura y las rutas disponibles en la API.

## ✅ Flujo recomendado

1. **Obtener UVL efectivo** desde la versión (guardado o generado desde la estructura).
2. **Editar UVL** en el cliente.
3. **Previsualizar cambios** con diff.
4. **Aplicar UVL** para crear una nueva versión estructurada.
5. (Opcional) **Sincronizar UVL** desde la estructura visual vigente.

---

## 📡 Endpoints

### 1) Obtener UVL efectivo

```
GET /api/v1/feature-models/{model_id}/versions/{version_id}/uvl
```

**Respuesta** (`source` indica el origen):

```json
{
  "version_id": "uuid",
  "feature_model_id": "uuid",
  "uvl_content": "namespace Model\n\nfeatures\n    Root\n        ...",
  "source": "stored"
}
```

---

### 2) Guardar UVL (edición paralela)

```
PUT /api/v1/feature-models/{model_id}/versions/{version_id}/uvl
```

**Body**:

```json
{
  "uvl_content": "namespace Model\n\nfeatures\n    Root\n        ..."
}
```

**Notas**:

- Solo el **owner** o **superuser** puede persistir cambios.
- Se validan mínimos: contenido no vacío y sección `features`.

---

### 3) Sincronizar UVL desde la estructura

```
POST /api/v1/feature-models/{model_id}/versions/{version_id}/uvl/sync-from-structure
```

Regenera y guarda el UVL a partir de la estructura actual de la versión.

---

### 4) Previsualizar diferencias (diff)

```
POST /api/v1/feature-models/{model_id}/versions/{version_id}/uvl/diff
```

**Body**:

```json
{
  "uvl_content": "namespace Model\n\nfeatures\n    Root\n        ..."
}
```

**Respuesta**:

```json
{
  "features_added": ["payment"],
  "features_removed": ["legacy"],
  "relations_added": [["a", "b", "requires"]],
  "relations_removed": [["c", "d", "excludes"]],
  "constraints_added": ["A | B"],
  "constraints_removed": ["!(X & Y)"]
}
```

---

### 5) Aplicar UVL a la estructura (nueva versión)

```
POST /api/v1/feature-models/{model_id}/versions/{version_id}/uvl/apply-to-structure
```

**Body**:

```json
{
  "uvl_content": "namespace Model\n\nfeatures\n    Root\n        ..."
}
```

Crea una **nueva versión** del modelo y persiste el UVL aplicado.

---

## ✅ Reglas UVL soportadas

### Features

- Bloques `mandatory`, `optional`, `alternative`, `or`.
- Indentación de **4 espacios** por nivel.
- Un único **root**.

### Constraints soportados

- **requires**: `A => B`
- **excludes**: `!(A & B)` o `!A | !B`
- Otras expresiones se almacenan como `Constraint.expr_text`.

---

## ⚠️ Validaciones clave

- Ciclos en el árbol.
- Features referenciadas en constraints deben existir.
- Grupos `alternative` requieren ≥ 2 hijos.

---

## 🔒 Permisos

Todas las rutas requieren autenticación. Las rutas de **guardar/sync/aplicar/diff** están restringidas a **owner** o **superuser**.
