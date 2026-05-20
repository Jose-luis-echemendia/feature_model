# ⚡ RESPUESTA DIRECTA: 5 Criterios Arquitectónicos

## La Pregunta

> ¿Qué criterio arquitectónico permitió diseñar evolución del FM que no invalide configuraciones antiguas?

## La Respuesta

**5 criterios integrados:**

### 1. COPY-ON-WRITE (Versionado Inmutable)

```python
# Cada versión es independiente
v1 [PUBLISHED]  # Congelada, nunca cambia
  ├─ Features: [Email, SMS]
  └─ Configs: [Basic] ← SIEMPRE válida

v2 [DRAFT]      # Editable, copia de v1
  ├─ Features: [Email, SMS] (copias)
  └─ Configs: [Basic] (copias editables)
```

**Beneficio**: Versión antigua INTACTA → configs VÁLIDAS SIEMPRE

---

### 2. MAPEO UUID↔INTEGER (Reproducibilidad)

```json
{
  "mapping": {
    "uuid_to_int": { "550e8400": 1, "6ba7b810": 2 },
    "int_to_uuid": { "1": "550e8400", "2": "6ba7b810" }
  }
}
```

**Beneficio**: Exportes reproducibles + compatibilidad externa

---

### 3. SEGREGACIÓN POR VERSIÓN (Aislamiento)

```sql
-- ✅ Correcto: Config ligada a versión específica
Configuration {
    feature_model_version_id: UUID  -- Explícita
}

-- Cambios en V2 NO afectan V1
```

**Beneficio**: Contextos completamente aislados

---

### 4. ESTADOS EXPLÍCITOS (Máquina de Estados)

```
[DRAFT] --publish()--> [PUBLISHED] --archive()--> [ARCHIVED]

PUBLISHED = INMUTABLE (garantía legal)
```

**Beneficio**: Imposible mutar versión publicada accidentalmente

---

### 5. CACHÉ GRANULAR (Performance)

```python
# Cambios en V2 solo invalidan caché de V2
invalidate_version_cache(version_id=v2)
# ↓
# Elimina: fm:tree:v2, fm:stats:v2
# Preserva: fm:tree:v1, fm:stats:v1 (sin tocar)
```

**Beneficio**: Performance aislado, escalabilidad O(log n)

---

## Por Qué Funciona

```
Feature Model evoluciona SIN INVALIDAR configs antiguas porque:

  v1 [PUBLISHED] ─────────────────┐
    Config "Basic" {Email, SMS}   │ INMUTABLE
    Snapshot congelado            │ AISLADA
    version_number = 1            │
                                  │
  v2 [PUBLISHED] ─────────────────┤ NUEVA VERSIÓN
    Config "Basic" {Email, SMS}   │ COPIA editable
    (copia de v1)                 │ (en DRAFT antes)
    version_number = 2            │
                                  │
  GARANTÍA: v1 nunca cambia → config SIEMPRE válida
```

---

## Tabla Comparativa

|                            | Sin Versiones | Versiones Simples | ✅ Implementado          |
| -------------------------- | ------------- | ----------------- | ------------------------ |
| Config antigua se invalida | ⚠️ SÍ         | ⚠️ RIESGO         | ✅ NUNCA                 |
| Trazabilidad               | ❌ NO         | ⚠️ Logs           | ✅ Snapshots + auditoría |
| Aislamiento                | ❌ NO         | ⚠️ Posible        | ✅ GARANTIZADO           |

---

## Código Prueba

**Archivo:** [backend/app/services/feature_model/fm_version_manager.py](../app/services/feature_model/fm_version_manager.py#L92-L125)

```python
async def create_new_version(self, source_version=None):
    """
    ✅ Copy-On-Write: Nueva versión copia estructura anterior
    """
    next_number = await self.repo.get_latest_version_number(...) + 1

    if source_version:
        # Copia features, constraints, configs (EDITABLE en DRAFT)
        new_version = await self.repo.create_new_version_from_existing(
            source_version=source_version
        )
        new_version.status = ModelStatus.DRAFT

    return new_version
```

**Archivo:** [backend/app/models/configuration.py](../app/models/configuration.py#L28-L52)

```python
class Configuration(BaseTable):
    # ✅ CLAVE: Config ligada a versión específica
    feature_model_version_id: UUID = Field(
        foreign_key="feature_model_versions.id"
    )

    # Si versión cambia → nueva Config en nueva versión
    # Antigua Config en v1 NO se ve afectada
```

---

## Garantía Formal

```
∀ configuration c ∈ version_v :
  (v.status = PUBLISHED) ⟹ c siempre válida

Porque:
  • c.feature_model_version_id = v.id (referencia específica)
  • v.snapshot es JSONB congelado (inmutable)
  • v' > v es versión independiente (no modifica v)
```

---

## 🎯 Resultado

✅ **Trazabilidad**: Completa (version_number + snapshots)
✅ **Compatibilidad**: Garantizada (aislamiento por versión)
✅ **Reproducibilidad**: Determinística (mapeo UUID↔Int)
✅ **Performance**: Escalable (caché granular)
✅ **Auditoría**: Exhaustiva (timestamps + created_by)

**Feature Model evoluciona indefinidamente sin invalidar configuraciones antiguas.**

---

## 📚 Documentación Completa

- [RESPUESTA_MECANISMO_EVOLUCION_FM.md](RESPUESTA_MECANISMO_EVOLUCION_FM.md) - Ejecutiva + código
- [ANALISIS_MECANISMO_EVOLUCION_FM.md](ANALISIS_MECANISMO_EVOLUCION_FM.md) - Análisis exhaustivo
- [VISUAL_ARQUITECTURA_EVOLUCION.md](VISUAL_ARQUITECTURA_EVOLUCION.md) - Diagramas visuales
- [GUIA_LECTURA_MECANISMO_EVOLUCION.md](GUIA_LECTURA_MECANISMO_EVOLUCION.md) - Ruta de aprendizaje
