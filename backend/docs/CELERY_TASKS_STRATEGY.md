# Estrategia de Implementación de Tareas Celery y Tareas Periódicas

## Objetivo

Definir una estrategia incremental para escalar el procesamiento asíncrono del sistema de Feature Models (UVL) con Celery + Redis, cubriendo:

- tareas on-demand de análisis/generación/exportación
- tareas periódicas para salud operativa y dashboards
- observabilidad, resiliencia e idempotencia

---

## Estado actual (base técnica)

- Celery ya está configurado en `backend/app/core/celery.py` con colas: `import`, `validation`, `default`, `maintenance`.
- `BEAT_SCHEDULE` existe en `backend/app/core/beat_schedule.py` pero sin jobs activos.
- Ya existe análisis asíncrono de modelo y endpoint de consulta de estado de tareas.

---

## Principios de diseño

1. **Idempotencia por tarea**: la misma tarea reintentada no debe corromper datos.
2. **Resultado consultable**: cada job debe exponer `task_id`, `status`, `result/error`.
3. **Desacoplar costo computacional**: peticiones HTTP rápidas; trabajo pesado en workers.
4. **Time limits y retries explícitos**: evitar workers colgados.
5. **Persistencia de artefactos**: reportes pesados en MinIO, no completos en Redis.

---

## Mapa de colas recomendado

- `import`: parseo/importación UVL, sincronizaciones grandes.
- `validation`: análisis SAT/SMT/estructural, comparación de versiones.
- `default`: generación optimizada y operaciones de negocio medias.
- `maintenance`: tareas programadas de limpieza, recomputación, monitoreo.

---

## Backlog de Tareas On-Demand (priorizado)

### P1 — Análisis completo UVL (ya implementado, consolidar)

**Task**: `run_feature_model_analysis`

- Entrada: `model_id`, `version_id`, `analysis_types`, `max_solutions`.
- Salida: satisfiability, dead/core/commonality, atomic sets, métricas.
- Mejora sugerida: guardar snapshot de resultados en BD para histórico.

### P1 — Generación masiva de configuraciones

**Task nueva**: `generate_bulk_configurations`

- Trigger: cuando `count` supere umbral (ej. > 20).
- Estrategias: `SAT_ENUM`, `CP_SAT`, `BDD`, `NSGA2`.
- Salida: lista de configuraciones + calidad (diversity, pairwise coverage).
- Persistencia: guardar resumen en BD y configuraciones en tabla dedicada/artefacto.

### P1 — Exportaciones pesadas + empaquetado

**Task nueva**: `export_feature_model_bundle`

- Genera UVL/JSON/DIMACS (y opcionalmente DOT/Mermaid).
- Empaqueta en ZIP y sube a MinIO.
- Retorna URL/clave de objeto.

### P1 — Comparación de versiones con reporte detallado

**Task nueva**: `compare_feature_model_versions`

- Entradas: `base_version_id`, `target_version_id`.
- Salida: cambios en dead/core, delta de configuraciones, riesgos.
- Reporte en JSON/Markdown, opcional PDF.

### P2 — Recomputar estadísticas tras cambios grandes

**Task nueva**: `recompute_version_statistics`

- Trigger: eventos de actualización masiva del modelo.
- Actualiza métricas derivadas para lectura rápida en UI.

### P2 — Optimización por objetivos avanzada

**Task nueva**: `optimize_configurations_by_objectives`

- Entrada: objetivos y pesos (p. ej. minimizar costo, maximizar cobertura).
- Estrategia: NSGA2/CP-SAT según tipo de objetivo.
- Salida: frente de Pareto + recomendaciones.

---

## Backlog de Tareas Periódicas (Celery Beat)

### P1 — Recalcular métricas de modelos activos (diario/nocturno)

**Task**: `refresh_active_models_metrics`

- Ejecutar por lotes (paginado) para evitar picos.
- Alimenta dashboards y salud del catálogo.

### P1 — Limpieza de jobs/resultados viejos en Redis (diario)

**Task**: `cleanup_stale_task_results`

- Limpia claves expiradas o huérfanas.
- Reduce costo/memoria en backend de resultados.

### P1 — Verificación de integridad (diario)

**Task**: `verify_models_integrity`

- Detecta versiones inconsistentes, constraints inválidos, referencias rotas.
- Genera alertas operativas (log estructurado + incidente).

### P2 — Pre-caching de modelos populares (noche)

**Task**: `precache_popular_models_analysis`

- Precalcula análisis de modelos más consultados.
- Mejora latencia percibida en UI.

### P2 — Monitoreo de recursos y rendimiento (cada hora)

**Task**: `collect_analysis_runtime_metrics`

- Captura tiempos por operación, tamaño de modelos, fallos por tipo.
- Base para alertas y capacity planning.

### P3 — Auditoría de calidad de datos (semanal)

**Task**: `audit_feature_model_data_quality`

- Duplicados, campos nulos críticos, cardinalidades sospechosas.

---

## Recomendaciones adicionales (importantes)

1. **Tabla de jobs de dominio** (`analysis_jobs`): trazabilidad funcional más allá del `task_id` de Celery.
2. **Correlación de logs**: `job_id`, `model_id`, `version_id`, `task_id` en cada log.
3. **Control de concurrencia por modelo**: lock por `model_id` para evitar carreras.
4. **Límites de entrada**: hard limits de `count`, `max_solutions`, tamaño UVL.
5. **Circuit breaker de operaciones pesadas**: fallback si SAT/BDD excede umbral.
6. **Retención de artefactos**: TTL y política de borrado en MinIO.
7. **Notificaciones UI** (opcional): WebSocket/SSE para progresos de job.

---

## Plan de implementación por fases

### Fase 1 (rápida, 1-2 sprints)

- Activar tareas P1 on-demand: bulk generation, export bundle, compare versions.
- Activar endpoints existentes de estado de tareas para UI.
- Definir contratos de respuesta homogéneos (`status`, `progress`, `result`, `error`).

### Fase 2 (operativa, 1 sprint)

- Activar Beat con 3 tareas: refresh metrics, cleanup results, integrity check.
- Añadir métricas de ejecución y dashboard técnico mínimo.

### Fase 3 (optimización, 1-2 sprints)

- Pre-caching nocturno de modelos populares.
- Optimización multiobjetivo con objetivos explícitos.
- Auditoría semanal de calidad de datos.

---

## Propuesta de naming de tareas

- `app.tasks.feature_model_analysis.run_feature_model_analysis`
- `app.tasks.feature_model_analysis.generate_bulk_configurations`
- `app.tasks.feature_model_analysis.export_feature_model_bundle`
- `app.tasks.feature_model_analysis.compare_feature_model_versions`
- `app.tasks.feature_model_analysis.recompute_version_statistics`
- `app.tasks.maintenance.refresh_active_models_metrics`
- `app.tasks.maintenance.cleanup_stale_task_results`
- `app.tasks.maintenance.verify_models_integrity`
- `app.tasks.maintenance.precache_popular_models_analysis`
- `app.tasks.maintenance.collect_analysis_runtime_metrics`

---

## Criterios de aceptación

- Toda operación pesada retorna `task_id` y puede consultarse por API.
- Jobs idempotentes con retries controlados y `time_limit`.
- Mínimo 3 tareas periódicas en producción con logs y métricas.
- Dashboard con métricas de salud de modelo y desempeño de tareas.
- Documentación de operación para soporte (runbook básico).

---

## Riesgos y mitigaciones

- **Sobrecarga de workers**: separar colas y ajustar concurrencia por tipo de job.
- **Resultados demasiado grandes en Redis**: mover artefactos a MinIO y guardar punteros.
- **Timeouts frecuentes**: dividir tareas, ajustar límites y fallback progresivo.
- **Inconsistencia por concurrencia**: locks por `model_id/version_id`.

---

## Próximo paso recomendado

Implementar primero `generate_bulk_configurations`, `export_feature_model_bundle` y `refresh_active_models_metrics`, porque aportan impacto funcional inmediato en UI y operación.
