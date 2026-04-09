# Evaluación arquitectónica formal del backend

## Alcance y criterio

Evaluación del backend actual en términos de:

- Fortalezas
- Cuellos de botella
- Riesgos
- Roadmap de evolución hacia **Clean/Hexagonal completa**

Priorización basada en **Impacto vs Esfuerzo** (escala 1–5):

- Impacto: 1 bajo, 5 muy alto
- Esfuerzo: 1 bajo, 5 muy alto
- Prioridad sugerida: Alto impacto + bajo/medio esfuerzo primero

---

## 1) Fortalezas arquitectónicas

1. **Modularidad real por carpetas y responsabilidades**
   - Separación en `api`, `services`, `repositories`, `core`, `tasks`, `models`.
   - Reduce acoplamiento accidental y facilita evolución incremental.

2. **Asincronía operacional madura**
   - Celery con colas especializadas (`import`, `validation`, `default`, `maintenance`).
   - Beat para tareas periódicas de mantenimiento y observabilidad.

3. **Infraestructura transversal centralizada**
   - Configuración, logging estructurado, redis/cache, s3/minio en `app/core`.
   - Buen punto de control operativo.

4. **Patrón repositorio consistente**
   - Permite encapsular persistencia y consultas complejas.

5. **Cobertura de cross-cutting concerns**
   - Middlewares + exception handlers globales bien definidos.

6. **Dominio de Feature Models modelado explícitamente**
   - Servicios dedicados a validación lógica, análisis estructural, exportación, versionado y generación.

---

## 2) Cuellos de botella detectados

1. **Dependencia directa de framework/infra en capas superiores**
   - Parte de la lógica de casos de uso aún vive en rutas.
   - Acoplamiento de servicios con detalles concretos de persistencia/infra.

2. **Duplicación de lógica de transformación/payload**
   - Construcción de payloads repetida entre servicios y tareas asíncronas.

3. **Límites de contexto parcialmente difusos**
   - Algunos módulos de `services`, `repositories` y `routes` se cruzan en responsabilidades.

4. **Persistencia de resultados de análisis no completamente normalizada**
   - Dependencia de resultados efímeros (Redis) para ciertos flujos operativos.

5. **Escalado de workers sin política de capacity planning formal**
   - Falta de umbrales SLO/SLA operativos documentados por tipo de tarea.

6. **Ausencia de puertos/adaptadores explícitos**
   - No hay contratos de aplicación totalmente desacoplados de infraestructura.

---

## 3) Riesgos arquitectónicos

### Riesgos técnicos

- **R1: Acoplamiento progresivo a FastAPI/SQLModel/Celery**
  - Efecto: dificultad para cambiar framework o probar reglas puras.
- **R2: Crecimiento de deuda por duplicación**
  - Efecto: inconsistencias funcionales y bugs en mantenimiento.
- **R3: Saturación de Redis** (cache + broker + result backend)
  - Efecto: degradación en latencia y colas.
- **R4: Variabilidad de tiempos en análisis complejos**
  - Efecto: timeouts, reintentos, costos operativos.

### Riesgos organizacionales

- **R5: Curva de mantenimiento para nuevos contribuidores**
  - Efecto: onboarding lento por mezcla de estilos (capas + servicios + tareas).
- **R6: Falta de métricas de arquitectura continuas**
  - Efecto: decisiones de evolución sin evidencia suficiente.

---

## 4) Matriz de priorización (Impacto vs Esfuerzo)

| ID  | Iniciativa                                                                | Impacto | Esfuerzo | Prioridad  | Justificación                                         |
| --- | ------------------------------------------------------------------------- | ------: | -------: | ---------- | ----------------------------------------------------- |
| I1  | Extraer casos de uso de rutas a `application/use_cases`                   |       5 |        3 | Alta       | Reduce acoplamiento y clarifica orquestación          |
| I2  | Definir puertos (`interfaces`) para repositorio, storage, cola, cache     |       5 |        4 | Alta       | Paso clave a Hexagonal real                           |
| I3  | Crear adaptadores en `infrastructure/adapters` para DB/Redis/MinIO/Celery |       5 |        4 | Alta       | Aísla dependencias tecnológicas                       |
| I4  | Eliminar duplicación de mapeos/payloads (mappers compartidos)             |       4 |        2 | Alta       | Ganancia rápida en mantenibilidad                     |
| I5  | Persistir resultados clave de análisis en DB (histórico)                  |       4 |        3 | Alta       | Trazabilidad y auditoría funcional                    |
| I6  | Definir políticas de resiliencia por tipo de tarea (retry/backoff/SLA)    |       4 |        2 | Alta       | Mejora estabilidad operativa inmediata                |
| I7  | Separar Redis lógico/físicamente por función (broker/result/cache)        |       4 |        3 | Media-Alta | Reduce contención y riesgo operacional                |
| I8  | Contratos de eventos de dominio (publicación/consumo)                     |       3 |        3 | Media      | Facilita evolución a arquitectura orientada a eventos |
| I9  | Medición continua de calidad arquitectónica (fitness functions)           |       4 |        3 | Media-Alta | Evita regresión de diseño                             |
| I10 | ADRs formales para decisiones arquitectónicas                             |       3 |        1 | Media-Alta | Bajo costo y alto valor de gobernanza                 |

---

## 5) Roadmap de evolución a Clean/Hexagonal completa

## Fase 0 — Estabilización rápida (2–4 semanas)

**Objetivo:** mejorar mantenibilidad y operación sin ruptura.

- [ ] Implementar mappers compartidos y retirar duplicación (I4)
- [ ] Formalizar políticas de resiliencia de tareas (I6)
- [ ] Crear ADRs de baseline arquitectónico (I10)

**Resultado esperado:** deuda técnica controlada y base documental de decisiones.

---

## Fase 1 — Limpieza de capa de aplicación (4–8 semanas)

**Objetivo:** separar claramente API de casos de uso.

- [ ] Introducir `application/use_cases/*` (I1)
- [ ] Reducir lógica de negocio en routes a validación de entrada/salida
- [ ] Estandarizar DTOs de aplicación y respuestas

**Resultado esperado:** rutas delgadas, casos de uso testeables y consistentes.

---

## Fase 2 — Hexagonalización progresiva (6–10 semanas)

**Objetivo:** invertir dependencias.

- [ ] Definir puertos (interfaces) en dominio/aplicación (I2)
- [ ] Implementar adaptadores de infraestructura (I3)
- [ ] Enlazar por inyección de dependencias a puertos, no a concreciones

**Resultado esperado:** dominio aislado de framework, test unitario más puro.

---

## Fase 3 — Robustez operativa y trazabilidad (4–6 semanas)

**Objetivo:** consolidar operación de producción.

- [ ] Persistir resultados clave de análisis y auditoría (I5)
- [ ] Segregar Redis por función o instancia (I7)
- [ ] Definir contratos de eventos de dominio y telemetría de punta a punta (I8)

**Resultado esperado:** mayor observabilidad, resiliencia y diagnóstico.

---

## Fase 4 — Gobernanza y fitness architecture (continuo)

**Objetivo:** evitar regresiones de diseño.

- [ ] Añadir quality gates arquitectónicos en CI (I9)
- [ ] Revisiones trimestrales de ADRs y deuda de acoplamiento
- [ ] Métricas base: acoplamiento entre módulos, complejidad, tiempo medio de cambio

**Resultado esperado:** arquitectura sostenible a largo plazo.

---

## 6) Recomendaciones ejecutivas

1. **Iniciar por Quick Wins**: I4 + I6 + I10.
2. **Primer salto estructural**: I1 (casos de uso) como antesala de I2/I3.
3. **No intentar “big bang refactor”**: migrar por vertical slices.
4. **Definir KPIs de éxito** desde el inicio:
   - Lead time de cambio
   - Tasa de incidentes por release
   - p95 de endpoints críticos
   - Tasa de reintentos/fallos de tareas

---

## Conclusión formal

La arquitectura actual es sólida para una etapa de crecimiento: modular, orientada a dominio y con asincronía madura. El paso a **Clean/Hexagonal completa** es factible sin disrupción si se ejecuta incrementalmente en 4 fases, priorizando desacoplamiento por puertos/adaptadores y gobernanza arquitectónica continua.
