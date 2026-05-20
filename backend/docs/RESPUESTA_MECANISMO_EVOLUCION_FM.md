# ✅ RESPUESTA: Mecanismo de Evolución del Feature Model

## La Pregunta

> **¿Qué criterio arquitectónico permitió diseñar un mecanismo de evolución del modelo que conserve la trazabilidad de las versiones y, al mismo tiempo, no invalide configuraciones previamente aceptadas cuando el FM crece o cambia?**

---

## 🎯 La Respuesta: 5 Criterios Integrados

### **1️⃣ VERSIONADO INMUTABLE (Copy-On-Write)**

Cada versión es un **snapshot congelado e inmutable**:

```python
# FeatureModelVersion nunca cambia una vez PUBLISHED
class FeatureModelVersion(BaseTable):
    version_number: int              # Secuencial: 1, 2, 3...
    status: ModelStatus              # DRAFT → PUBLISHED → ARCHIVED
    snapshot: dict                   # Congelado en JSONB

    features: list["Feature"]        # Pertenecen a ESTA versión
    configurations: list["Configuration"]  # Ligadas a ESTA versión
```

**Beneficio**: Versión antigua NUNCA cambia → configuraciones antiguas siempre válidas.

---

### **2️⃣ MAPEO ESTABLE UUID↔INTEGER**

Cada snapshot almacena mapeo bidireccional:

```json
{
  "version_number": 2,
  "mapping": {
    "uuid_to_int": {
      "550e8400-e29b...": 1,
      "6ba7b810-9dad...": 2,
      "6ba7b811-9dad...": 3
    },
    "int_to_uuid": {
      "1": "550e8400-e29b...",
      "2": "6ba7b810-9dad...",
      "3": "6ba7b811-9dad..."
    }
  }
}
```

**Beneficio**: Exportes reproducibles + compatibilidad con herramientas externas (SPLOTGenesis, FeatureIDE).

---

### **3️⃣ SEGREGACIÓN POR VERSIÓN (Aggregate Root Pattern)**

Cada elemento pertenece a una versión específica:

```sql
-- ❌ MAL: Features flotantes sin versión
Feature { name, type }

-- ✅ BIEN: Features vinculadas a versión
Feature {
    name,
    type,
    feature_model_version_id UUID  -- ← CLAVE
}

Configuration {
    name,
    feature_model_version_id UUID  -- ← Ligada a versión
}
```

**Beneficio**: Cambios en v2 no afectan datos de v1. Aislamiento total.

---

### **4️⃣ MÁQUINA DE ESTADOS EXPLÍCITA**

Estados de ciclo de vida rigurosos:

```
[DRAFT] --publish()--> [PUBLISHED] --archive()--> [ARCHIVED]
  ↑
  └─────── restore() ◄─────┘
```

| Estado        | Mutable      | Snapshot | Configs    |
| ------------- | ------------ | -------- | ---------- |
| **DRAFT**     | ✏️ Editable  | ❌ No    | Creables   |
| **PUBLISHED** | 🔒 Inmutable | ✅ Sí    | Activas    |
| **ARCHIVED**  | 🔒 Inmutable | ✅ Sí    | Históricas |

**Beneficio**: Garantía legal de que PUBLISHED nunca cambia.

---

### **5️⃣ CACHÉ INVALIDACIÓN GRANULAR**

Invalidar solo lo necesario:

```python
# Cuando se modifica Feature en v2:
# ✅ Invalida: fm:tree:v2, fm:stats:v2
# ✅ Preserva: fm:tree:v1, fm:stats:v1 (sin tocar)

async def invalidate_version_cache(version_id: UUID):
    pattern = f"fm:*:{version_id}"
    await redis.delete(*keys)  # Solo esta versión
```

**Beneficio**: Performance aislado. Cambios en v2 no ralentizan acceso a v1.

---

## 🔄 CÓMO FUNCIONAN JUNTOS

```
Usuario agrega feature "Push" al FM:

1. GET /feature-models/{id}/versions/latest
   → Retorna v1 [PUBLISHED]

2. POST /feature-models/{id}/versions
   → Crea v2 [DRAFT] (copia de v1 con Copy-On-Write)

3. POST /feature-models/{id}/versions/2/features
   → Agrega "Push" solo en v2
   → Invalida caché de v2
   → v1 totalmente intacto

4. POST /feature-models/{id}/versions/2/publish
   → Genera snapshot inmutable
   → Guarda mapeo UUID↔Int
   → Cambia v2 a [PUBLISHED]

RESULTADO:
  v1 [PUBLISHED]: Snapshot antiguo + Configs antiguas = SIEMPRE VÁLIDAS
  v2 [PUBLISHED]: Snapshot nuevo + Configs nuevas = Independientes
```

---

## 💡 ¿POR QUÉ FUNCIONA?

| Requisito                        | Cómo se satisface                                                |
| -------------------------------- | ---------------------------------------------------------------- |
| **Trazabilidad de versiones**    | `version_number` secuencial + snapshots + timestamps + auditoría |
| **No invalida configs antiguas** | Configs ligadas a `version_id` específico → aisladas por versión |
| **El FM puede crecer**           | Nuevas versiones → copy-on-write → sin afectar anteriores        |
| **Reproducibilidad**             | Snapshot congelado + mapeo determinístico                        |
| **Performance**                  | Caché granular + queries aisladas por versión                    |

---

## 📊 COMPARACIÓN

| Aspecto                    | Sin versionado | Versionado simple | ✅ Implementación        |
| -------------------------- | -------------- | ----------------- | ------------------------ |
| Config antigua se invalida | ⚠️ SÍ          | ⚠️ RIESGO         | ✅ NUNCA                 |
| Trazabilidad               | ❌ NO          | ⚠️ Logs           | ✅ Snapshots + auditoría |
| Cambios futuros aislados   | ❌ NO          | ⚠️ Posible        | ✅ SÍ                    |
| Reproducibilidad           | ❌ NO          | ⚠️ Difícil        | ✅ Garantizada           |

---

## 📝 EVIDENCIA EN CÓDIGO

**Archivo principal:** [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py#L92-L125)

```python
async def create_new_version(self, source_version=None):
    """
    Copy-On-Write: Crea versión nueva clonando la anterior.
    """
    next_number = await self.repo.get_latest_version_number(...) + 1

    if source_version:
        # ✅ Copia toda estructura de la anterior
        new_version = await self.repo.create_new_version_from_existing(
            source_version=source_version
        )
        new_version.status = ModelStatus.DRAFT

    return new_version
```

**Archivo modelo:** [backend/app/models/configuration.py](backend/app/models/configuration.py#L28-L52)

```python
class Configuration(BaseTable):
    # ✅ CLAVE: Ligada a versión específica
    feature_model_version_id: UUID = Field(
        foreign_key="feature_model_versions.id"
    )
```

---

## 🎓 PRINCIPIOS ARQUITECTÓNICOS DETRÁS

1. **Event Sourcing**: Cada versión es un "evento" inmutable del modelo
2. **Aggregate Root Pattern**: FeatureModelVersion es raíz que contiene todo
3. **CQRS implicit**: Separación clara entre lectura (snapshot) y escritura (DRAFT)
4. **Immutability by Design**: Estado controlado, no mutación silenciosa
5. **Temporal Database**: Snapshots = registro temporal del estado

---

## ✨ RESULTADO FINAL

> **El Feature Model puede evolucionar indefinidamente sin NUNCA invalidar configuraciones previamente aceptadas**, porque cada versión es un **contexto aislado e inmutable** vinculado explícitamente a sus configuraciones.

**Trazabilidad**: ✅ Completa (snapshots + versioning)
**Compatibilidad**: ✅ Garantizada (aislamiento por versión)
**Reproducibilidad**: ✅ Determinística (mapeo UUID↔Int)
**Performance**: ✅ Escalable (caché granular)
**Auditoría**: ✅ Exhaustiva (timestamps + created_by)
