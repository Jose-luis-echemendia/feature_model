# ⚡ QUICKSTART: 30 Segundos

## La Pregunta

> ¿Por qué las configuraciones antiguas NO se invalidan cuando el FM cambia?

## La Respuesta

### 5 Criterios (UNO en cada línea)

| #   | ¿Qué?                 | ¿Por qué funciona?                                  |
| --- | --------------------- | --------------------------------------------------- |
| 1   | **Copy-On-Write**     | Nueva versión = copia editable, anterior NUNCA muta |
| 2   | **UUID↔Integer**      | Mapeo determinístico = reproducibilidad             |
| 3   | **Versión explícita** | Config→version_id = aislada de otras versiones      |
| 4   | **Estados rígidos**   | PUBLISHED = INMUTABLE garantizado                   |
| 5   | **Caché granular**    | Cambios en v2 no tocan caché de v1                  |

---

## Dibujo en 10 Segundos

```
V1 [PUBLISHED]                    V2 [PUBLISHED]
Config "Basic": {Email, SMS} ✅    Config "Basic": {Email, SMS} (copy)
Congelado = NUNCA cambia           Independiente

GARANTÍA: Config en V1 es SIEMPRE válida
```

---

## Código en 3 Líneas

```python
# Crear versión nueva (copy-on-write)
new_version = await manager.create_new_version(source_version=v1)

# Config ligada a versión específica (no flotante)
config.feature_model_version_id = v1.id  # ← Explícita
```

---

## Por Qué

```
Config "Basic" referencia V1.id
V1 es INMUTABLE (estado PUBLISHED)
V2 es independiente (copy, no referencia)
∴ Config "Basic" en V1 siempre válida
```

---

## ✅ Resultado

FM evoluciona SIN invalidar configuraciones antiguas.

---

## 📚 Quiero Saber Más

- **1 minuto**: [RESPUESTA_FINAL_5_CRITERIOS.md](RESPUESTA_FINAL_5_CRITERIOS.md)
- **5 minutos**: [VISUAL_ARQUITECTURA_EVOLUCION.md](VISUAL_ARQUITECTURA_EVOLUCION.md)
- **15 minutos**: [RESPUESTA_MECANISMO_EVOLUCION_FM.md](RESPUESTA_MECANISMO_EVOLUCION_FM.md)
- **45 minutos**: [ANALISIS_MECANISMO_EVOLUCION_FM.md](ANALISIS_MECANISMO_EVOLUCION_FM.md)
