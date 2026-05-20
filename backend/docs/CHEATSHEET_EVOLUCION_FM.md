# 🎯 CHEAT SHEET: Mecanismo de Evolución del FM

## La Pregunta

```
¿Por qué el FM evoluciona sin invalidar configuraciones antiguas?
```

## La Respuesta en 1 Imagen

```
V1 [PUBLISHED]              V2 [PUBLISHED]
├─Config "Basic"            ├─Config "Basic" (copy)
│ {Email, SMS}              │ {Email, SMS}
│ ✅ VÁLIDA SIEMPRE          │ ✅ Independiente
│                           │
├─Snapshot: CONGELADO       ├─Snapshot: CONGELADO
├─Features: [Email, SMS]    ├─Features: [Email, SMS, Push]
└─Status: INMUTABLE         └─Status: INMUTABLE

    ↓
GARANTÍA: V1 nunca cambia
        = Config en V1 siempre válida
```

---

## Los 5 Criterios

### 1️⃣ Copy-On-Write

```
new_version = create_new_version(source_version=v1)
        ↓
Copia features, constraints, configs de v1
v1 permanece INTACTA
new_version editable en DRAFT
```

### 2️⃣ Mapeo UUID↔Integer

```
{
  "550e8400": 1  ← UUID → Integer (determinístico)
  "6ba7b810": 2
}
Mapeo guardado en snapshot = reproducible siempre
```

### 3️⃣ Segregación por Versión

```
Config {
  feature_model_version_id: UUID  ← CLAVE
}
Config ligada a v1 ≠ config en v2
```

### 4️⃣ Estados Explícitos

```
[DRAFT] → [PUBLISHED] → [ARCHIVED]
editable   inmutable    histórico

PUBLISHED = no muta (garantía legal)
```

### 5️⃣ Caché Granular

```
invalidate(version_id=v2)
├─Elimina: fm:tree:v2, fm:stats:v2
└─Preserva: fm:tree:v1 (sin tocar)
```

---

## Código Clave (Copy-Paste)

### Crear versión

```python
manager = FeatureModelVersionManager(session, feature_model)
new_version = await manager.create_new_version(source_version=latest)
```

### Publicar versión

```python
published = await manager.publish_version(version, validate=True)
# ↓ Genera snapshot + congela estado
```

### Config vinculada a versión

```python
config = Configuration(
    feature_model_version_id=version.id,  # ← Explícita
    name="Basic",
    features=[...]
)
```

---

## Flujo Visual: Agregar Feature

```
1. GET /versions/latest
   └─ V1 [PUBLISHED] (congelada)

2. POST /versions
   └─ V2 [DRAFT] (copia de v1)

3. POST /versions/2/features {name: "Push"}
   ├─ INSERT Feature "Push" en V2
   ├─ V1 INTACTA ✅
   └─ Config "Basic" en V1 SIGUE VÁLIDA ✅

4. POST /versions/2/publish
   ├─ Generar snapshot
   ├─ Congelar V2
   └─ V2 ahora inmutable ✅
```

---

## Garantías

| Garantía            | Mecanismo                           |
| ------------------- | ----------------------------------- |
| V1 nunca muta       | Status = PUBLISHED (inmutable)      |
| Config en V1 válida | Config.version_id = V1.id (aislada) |
| Reproducible        | Mapeo UUID→Int determinístico       |
| Performance         | Caché granular (no toca v1)         |
| Auditable           | Snapshots + timestamps              |

---

## Comparación: Alternativas

| Aspecto            | ❌ Sin versiones | ⚠️ Simple | ✅ Actual |
| ------------------ | ---------------- | --------- | --------- |
| Config se invalida | SÍ               | RIESGO    | NUNCA     |
| Trazabilidad       | NO               | Logs      | Snapshots |
| Reproducible       | NO               | Difícil   | SÍ        |

---

## ¿Qué Pasa Si...?

### ...cambio Feature en V2?

```
V2 cambio → invalidar caché V2 → V1 sin afectar ✅
```

### ...agrego nueva Config?

```
Puedo crearla en V2 (editable) → luego publicar ✅
```

### ...necesito versión anterior?

```
V1 está congelada → Config en V1 SIEMPRE válida ✅
```

### ...modifico V1?

```
IMPOSIBLE (Status = PUBLISHED = inmutable) 🔒
```

---

## Archivos Clave

| Archivo                  | Qué buscar                              |
| ------------------------ | --------------------------------------- |
| fm_version_manager.py    | create_new_version(), publish_version() |
| configuration.py (model) | feature_model_version_id field          |
| configuration.py (repo)  | create(), update()                      |

---

## Enlaces Rápidos

- **5 min**: [RESPUESTA_FINAL_5_CRITERIOS.md](backend/docs/RESPUESTA_FINAL_5_CRITERIOS.md)
- **10 min**: [VISUAL_ARQUITECTURA_EVOLUCION.md](backend/docs/VISUAL_ARQUITECTURA_EVOLUCION.md)
- **15 min**: [RESPUESTA_MECANISMO_EVOLUCION_FM.md](backend/docs/RESPUESTA_MECANISMO_EVOLUCION_FM.md)
- **30 seg**: [QUICKSTART_30SEGUNDOS.md](backend/docs/QUICKSTART_30SEGUNDOS.md)

---

## Conclusión

✅ **FM evoluciona indefinidamente sin invalidar configs antiguas**

porque:

1. Copy-On-Write = v1 nunca muta
2. Segregación = config aislada a versión
3. Estados = PUBLISHED inmutable
4. Caché = cada versión independiente
5. Mapeo = reproducible

**GARANTÍA**: Config en V1 siempre válida.
