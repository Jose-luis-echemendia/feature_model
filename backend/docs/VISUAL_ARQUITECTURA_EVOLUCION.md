# 📐 ARQUITECTURA DE EVOLUCIÓN: Visual Summary

## Pregunta

> ¿Qué criterio arquitectónico permite que el FM evolucione sin invalidar configuraciones antiguas?

---

## Diagrama: Arquitectura de Versiones

```
╔════════════════════════════════════════════════════════════════╗
║                    FEATURE MODEL (raíz)                        ║
║                                                                ║
║  name: "E-Commerce FM"                                        ║
║  owner: user123                                               ║
║  domain: "E-Commerce"                                         ║
╚═════════════════════╤════════════════════════════════════════╝
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌────────┐   ┌────────┐   ┌────────┐
    │ Ver 1  │   │ Ver 2  │   │ Ver 3  │
    │ [PUB]  │   │ [PUB]  │   │[DRAFT] │
    └────────┘   └────────┘   └────────┘
        │             │             │
        │   Snapshot  │  Snapshot   │
        │   Congelado │  Congelado  │ (aún no)
        │             │             │
        ├─Features    ├─Features    ├─Features
        ├─Constraints ├─Constraints ├─Constraints
        ├─Relations   ├─Relations   ├─Relations
        └─Configs     └─Configs     └─Configs
            (act)       (act)          (new)


Cada versión = CONTEXTO AISLADO E INMUTABLE
```

---

## Diagrama: Timeline de Evolución

```
TIEMPO ──────────────────────────────────────────────────>

V1 [PUBLISHED]
├─ Features: Email, SMS
├─ Config "Basic": {Email, SMS}
├─ Snapshot: CONGELADO ✅
└─ Estado: NUNCA cambia

        V2 [PUBLISHED]
        ├─ Features: Email, SMS, Push (NUEVA)
        ├─ Config "Basic": {Email, SMS} (COPIA de V1)
        ├─ Config "Premium": {Email, SMS, Push} (NUEVA)
        ├─ Snapshot: CONGELADO ✅
        └─ Estado: NUNCA cambia

                V3 [DRAFT]
                ├─ Features: Email, SMS, Push, WebPush (NUEVA)
                ├─ Config "Basic": {Email, SMS} (editable)
                ├─ Snapshot: NO (se genera al publicar)
                └─ Estado: EDITABLE


GARANTÍA: Config "Basic" en V1 es válida PARA SIEMPRE
         porque V1.snapshot está congelado
```

---

## Tabla: Estados y Mutabilidad

```
┌──────────┬──────────┬────────┬──────────────┬────────────┐
│ Estado   │ Mutable  │Snapshot│ Config Nueva │ Acceso     │
├──────────┼──────────┼────────┼──────────────┼────────────┤
│ DRAFT    │ ✏️ Editable│ ❌ NO │ ✅ Sí        │ Propietario│
│          │           │        │              │            │
│PUBLISHED │ 🔒 INMUT  │ ✅ SÍ  │ ✅ Sí (copy) │ Público    │
│          │           │        │              │            │
│ ARCHIVED │ 🔒 INMUT  │ ✅ SÍ  │ ❌ No       │ Solo Audit │
└──────────┴──────────┴────────┴──────────────┴────────────┘
```

---

## Tabla: Los 5 Criterios Arquitectónicos

```
┌─────────────┬──────────────────┬─────────────────────┐
│ Criterio    │ Mecanismo        │ Beneficio           │
├─────────────┼──────────────────┼─────────────────────┤
│ 1. Copy-On  │ Copia estructura │ Versión antigua     │
│    Write    │ de anterior      │ NUNCA cambia        │
├─────────────┼──────────────────┼─────────────────────┤
│ 2. Mapeo    │ UUID ↔ Integer   │ Reproducibilidad    │
│    Estable  │ determinístico   │ de exportes         │
├─────────────┼──────────────────┼─────────────────────┤
│ 3.Segreg.  │ Config→version_id │ Aislamiento total   │
│    por Ver. │ explícita        │ entre versiones    │
├─────────────┼──────────────────┼─────────────────────┤
│ 4. Estados  │ DRAFT→PUB→ARCH   │ Garantía legal      │
│    Explícit │ (máquina estados)│ de inmutabilidad   │
├─────────────┼──────────────────┼─────────────────────┤
│ 5. Caché    │ Invalidar solo   │ Performance        │
│    Granular │ versión afectada │ aislado            │
└─────────────┴──────────────────┴─────────────────────┘
```

---

## Código: Copy-On-Write en Acción

```python
# ANTES: No hay versión 2
FeatureModel {
  id: "fm-123"
  versions: [FeatureModelVersion {
    id: "v1-uuid",
    version_number: 1,
    status: "PUBLISHED",
    features: [Feature "Email", Feature "SMS"],
    configurations: [Config "Basic"]
  }]
}

# USUARIO: "Agregar Push Notifications"
POST /feature-models/fm-123/versions
  → Crea nueva versión con Copy-On-Write


# DESPUÉS: Versión 2 es COPIA de V1
FeatureModel {
  id: "fm-123"
  versions: [
    FeatureModelVersion {
      version_number: 1,
      status: "PUBLISHED",
      snapshot: {congelado},  # ← INMUTABLE
      features: [Email, SMS]
      configurations: [Basic] # ← NUNCA cambiará
    },
    FeatureModelVersion {
      version_number: 2,
      status: "DRAFT",
      snapshot: null,         # ← Se genera al publicar
      features: [Email, SMS]  # ← Copias editables
      configurations: [Basic] # ← Copias editables
    }
  ]
}

# USUARIO: Agrega "Push" en V2
POST /feature-models/fm-123/versions/v2/features
  name: "Push"

→ INSERT Feature "Push" (version_id: v2)
→ V1 TOTALMENTE INTACTO ✅

# V2 se publica
POST /feature-models/fm-123/versions/v2/publish
  → Genera snapshot (mapeo UUID→Int, stats, etc)
  → Congela: status = "PUBLISHED"
  → Ahora V2 también es inmutable ✅
```

---

## Garantías: Lógica Formal

```
Propiedad 1: Configuraciones Antiguas Nunca Se Invalidan
──────────────────────────────────────────────────────

  ∀ configuration c ∈ version_v :
    (v.status = PUBLISHED)
    ⟹ c siempre válida

  Porque:
    c.feature_model_version_id = v.id  (referencia específica)
    v.snapshot es JSONB congelado
    ∀ version v' > v : v' es independiente (no modifica v)


Propiedad 2: Trazabilidad Completa
───────────────────────────────────

  ∀ cambio en FM ∃ :
    version_number que lo numera
    snapshot que lo congeliza
    created_by_id que lo acredita
    created_at que lo sitúa


Propiedad 3: Reproducibilidad
──────────────────────────────

  snapshot.mapping.uuid_to_int = f(version.features)
  f es DETERMINÍSTICA
  ⟹ Export_UVL(snapshot) siempre produce MISMO archivo


Propiedad 4: Aislamiento de Performance
────────────────────────────────────────

  cache(version_i) NOT AFFECTED BY modificaciones en version_j  (i ≠ j)
  ⟹ Escalabilidad O(log n) según número de versiones
```

---

## Flujo: Agregar Nueva Feature

```
┌─────────────────────────────────────────────────────────┐
│ USUARIO: "Quiero agregar Push Notifications"            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Obtener versión actual                              │
│    GET /feature-models/{id}/versions/latest            │
│    ↓                                                   │
│    FeatureModelVersion 1 [PUBLISHED]                   │
│    - Features: [Email, SMS]                            │
│    - Config "Basic": {Email, SMS}                      │
│    - Snapshot: CONGELADO ✅                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Crear nueva versión (copy-on-write)                 │
│    POST /feature-models/{id}/versions                  │
│    ↓                                                   │
│    FeatureModelVersionManager.create_new_version(      │
│        source_version=v1                              │
│    )                                                   │
│    ↓                                                   │
│    ✅ Versión 2 [DRAFT] creada                         │
│    - Copia: Features [Email, SMS]                      │
│    - Copia: Config "Basic" {Email, SMS}                │
│    - Editable: status = DRAFT                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Agregar nueva feature en v2                         │
│    POST /feature-models/{id}/versions/2/features      │
│    {name: "Push"}                                      │
│    ↓                                                   │
│    INSERT Feature "Push" (version_id: v2)             │
│    ↓                                                   │
│    Invalidar caché: fm:*:v2                            │
│    ↓                                                   │
│    ✅ V1 TOTALMENTE INTACTO                             │
│    ✅ Config "Basic" en V1 SIGUE VÁLIDA                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Validar versión 2                                   │
│    POST /feature-models/{id}/versions/2/validate      │
│    ↓                                                   │
│    FeatureModelLogicalValidator:                       │
│    - Chequear constraints consistency                  │
│    - Verificar no-dead-features                        │
│    - Validar cardinalidades                            │
│    ↓                                                   │
│    ✅ V2 es válida                                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Publicar versión 2                                  │
│    POST /feature-models/{id}/versions/2/publish       │
│    ↓                                                   │
│    FeatureModelVersionManager.publish_version():       │
│    a) Generar snapshot:                                │
│       - Mapeo UUID ↔ Integer (1→Email, 2→SMS, 3→Push) │
│       - Árbol de features                              │
│       - Estadísticas                                   │
│    b) Guardar snapshot en BD (CONGELADO)              │
│    c) Cambiar estado: DRAFT → PUBLISHED                │
│    ↓                                                   │
│    ✅ V2 [PUBLISHED] ahora INMUTABLE                    │
│    ✅ Snapshot guardado = reproducible                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ RESULTADO FINAL                                         │
│                                                         │
│ V1 [PUBLISHED]                                          │
│   Features: [Email, SMS]                                │
│   Config "Basic": {Email, SMS} ← NUNCA cambiará        │
│   Snapshot: CONGELADO                                   │
│                                                         │
│ V2 [PUBLISHED]                                          │
│   Features: [Email, SMS, Push]                          │
│   Config "Basic": {Email, SMS} (copia de V1)            │
│   Config "Premium": {Email, SMS, Push} (NUEVA)          │
│   Snapshot: CONGELADO                                   │
│                                                         │
│ TRAZABILIDAD: ✅                                         │
│ COMPATIBILIDAD: ✅                                       │
│ REPRODUCIBILIDAD: ✅                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Comparación: Arquitecturas

```
┌─────────────────────┬─────────────────────┬────────────────────┐
│ SIN VERSIONADO      │ VERSIONADO SIMPLE   │ ✅ IMPLEMENTADO     │
├─────────────────────┼─────────────────────┼────────────────────┤
│ Modelo flotante     │ ID de versión       │ FeatureModelVersion│
│ (un solo registro)  │ (no aislado)        │ (agregado completo)│
│                     │                     │                    │
│ ❌ Config se rompe  │ ⚠️ Riesgo de        │ ✅ Config vinculada│
│    al cambiar       │   inconsistencia    │    a versión       │
│                     │                     │                    │
│ ❌ No hay           │ ⚠️ Solo logs        │ ✅ Snapshots +     │
│    trazabilidad     │   (no reproducible) │    auditoría       │
│                     │                     │                    │
│ ❌ Cambios          │ ⚠️ Posible          │ ✅ Garantizado     │
│    rompen todo      │   si compatible     │    aislado         │
│                     │                     │                    │
│ ❌ Performance      │ ⚠️ Costo lineal     │ ✅ Caché granular  │
│    degrada          │   por cambios       │    (O(log n))      │
└─────────────────────┴─────────────────────┴────────────────────┘
```

---

## Keywords Clave

| Concepto           | Definición                                                        |
| ------------------ | ----------------------------------------------------------------- |
| **Copy-On-Write**  | Copia estructura al crear nueva versión, solo lo que se modifica  |
| **Snapshot**       | Foto congelada del estado completo (inmutable, reproducible)      |
| **Aggregate Root** | FeatureModelVersion contiene todas sus features y configuraciones |
| **Immutability**   | Una vez PUBLISHED, nunca cambia (garantía legal)                  |
| **Segregation**    | Cada versión es contexto independiente aislado                    |
| **Trazabilidad**   | version_number + snapshots + timestamps + auditoría               |
| **Determinismo**   | Mapeo UUID↔Integer siempre produce mismo resultado                |

---

## 🎓 Conclusión

**5 criterios arquitectónicos trabajan en sinergia:**

1. ✅ **Copy-On-Write**: Versión antigua nunca muta
2. ✅ **Mapeo UUID↔Int**: Reproducibilidad garantizada
3. ✅ **Segregación por Versión**: Aislamiento total
4. ✅ **Estados Explícitos**: Máquina de estados rigurosa
5. ✅ **Caché Granular**: Performance aislado

**Resultado**: Feature Model evoluciona indefinidamente sin NUNCA invalidar configuraciones antiguas.

---

## 📚 Documentación Completa

- [ANALISIS_MECANISMO_EVOLUCION_FM.md](ANALISIS_MECANISMO_EVOLUCION_FM.md) - Análisis exhaustivo
- [RESPUESTA_MECANISMO_EVOLUCION_FM.md](RESPUESTA_MECANISMO_EVOLUCION_FM.md) - Respuesta ejecutiva
- [CRC_BACKEND.md](CRC_BACKEND.md) - Responsabilidades por componente
- [CACHE_INVALIDATION_EXAMPLES.md](CACHE_INVALIDATION_EXAMPLES.md) - Estrategia de caché
