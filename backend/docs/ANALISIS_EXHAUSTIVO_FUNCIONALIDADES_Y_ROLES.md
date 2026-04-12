# Análisis exhaustivo de funcionalidades del sistema y modelo de roles

Fecha: 2026-04-12

## 1) Objetivo

Documentar, de forma integral, las funcionalidades implementadas del backend y explicar cómo el sistema de roles controla la lectura/escritura por entidad.

---

## 2) Alcance y fuentes usadas

Este análisis se basa en:

- Inventario funcional backend (127 endpoints + 6 capacidades transversales).
- Arquitectura backend (monolito modular en capas, DDD pragmático, Celery/Redis para asincronía).
- Documento de roles inicial ([backend/docs/user_role.md](backend/docs/user_role.md)).

**Cobertura funcional considerada:**

- **127 requisitos funcionales** expuestos por API REST/WS.
- **6 capacidades transversales** observables (settings, caché, jobs, MinIO, exportables).
- **Total:** 133 capacidades funcionales documentadas.

---

## 3) Análisis exhaustivo de funcionalidades del sistema

## 3.1 Capacidades núcleo (por macro-módulo)

### A. Plataforma y operación

- Health check simple y estado profundo del sistema (DB, Redis, Celery, MinIO, host).
- Endpoints utilitarios para diagnóstico, lectura de settings y pruebas controladas.
- Limpieza de caché con invalidación por patrones y reglas de escritura.

### B. Identidad y acceso

- Login JWT, test de token vigente, recuperación y reset de contraseña.
- Gestión de usuarios completa: CRUD, activación/desactivación, búsqueda, cambio de rol, perfil propio.
- Control de acceso por rol con reglas de ownership, colaboración y estado de publicación.

### C. Gestión de dominio

- CRUD de dominios con activación/desactivación.
- Consulta de dominios con modelos asociados.
- Restricciones de eliminación por dependencias.

### D. Ciclo de vida de Feature Models

- CRUD de feature models.
- Gestión de estado activo/inactivo.
- Versionado robusto (creación, publicación, archivado, restauración, consulta de latest).
- Operaciones de copia y evolución orientadas a trazabilidad de cambios.

### E. Edición estructural del modelo

- CRUD completo sobre:
  - Features
  - Feature Groups
  - Feature Relations
  - Constraints
- Operaciones avanzadas como movimiento de nodos y edición copy-on-write.
- Consulta de subárboles, relaciones y tags por feature.

### F. UVL (interoperabilidad textual/estructural)

- Obtener UVL efectivo.
- Guardar UVL validado.
- Sincronizar UVL desde estructura.
- Aplicar UVL para generar estructura/versiones.
- Calcular diff UVL vs estructura antes de materializar cambios.

### G. Validación y análisis avanzado

- Validación lógica, estructural y de configuración.
- Validación integral (full pipeline).
- Resumen de análisis y comparación de versiones.
- Métricas y estadísticas por versión + latest.
- WebSocket de estadísticas en tiempo real.

### H. Asincronía y tareas

- Lanzamiento de análisis batch y operaciones pesadas.
- Export bundle asíncrono, comparación batch, recomputación de stats.
- Estado/progreso/cancelación de tareas genéricas y especializadas.
- Modelo de ejecución desacoplado vía Celery + Redis.

### I. Configuraciones (producto derivado)

- CRUD de configuraciones.
- Validación previa sin persistencia.
- Generación automática de configuraciones válidas.
- Optimización multicriterio (estrategias avanzadas).
- Opciones por etapas (can/must select/deselect) para guiado progresivo.

### J. Recursos, tags y soporte documental

- CRUD parcial de recursos y tags (según rol/ownership).
- Asociación/desasociación de tags a features.
- Gestión de artefactos exportables y soporte de object storage.
- Guías de acceso a documentación interna.

---

## 3.2 Características no funcionales observables (soporte a lo funcional)

- Arquitectura en capas con separación API/servicios/repositorios/infra.
- Seguridad por rol + ownership + estado de entidad (draft/review/published).
- Escalabilidad operativa con ejecución asíncrona.
- Observabilidad mediante logging estructurado y endpoints de estado.
- Performance funcional mediante cacheo e invalidación automática.
- Integración de almacenamiento de objetos para exportaciones/artefactos.

---

## 4) Sistema de roles: lectura y escritura por entidad

## 4.1 Interpretación de operaciones

- **Lectura (R):** permisos de consulta/listado.
- **Escritura (W):** crear/actualizar/eliminar (POST/PUT/PATCH/DELETE).
- Cuando aplica, se indica si la escritura es **global** o **acotada** (propios, colaboraciones, publicados, públicos).

---

## 4.2 Tabla resumen (R/W por rol y por tabla)

> Convención en celdas: **R=Lectura / W=Escritura**.

| Tabla / Entidad              | ADMIN                                 | MODEL_DESIGNER                                      | MODEL_EDITOR                                           | REVIEWER                                              | CONFIGURATOR                                     | VIEWER                   |
| ---------------------------- | ------------------------------------- | --------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------ | ------------------------ |
| **User**                     | R=Sí / W=Sí (global)                  | R=No especificado / W=No especificado               | R=No especificado / W=No especificado                  | R=No especificado / W=No especificado                 | R=No especificado / W=No especificado            | R=No / W=No              |
| **Domain**                   | R=Sí / W=Sí (global)                  | R=No especificado / W=No especificado               | R=No especificado / W=No especificado                  | R=No especificado / W=No especificado                 | R=No especificado / W=No especificado            | R=No / W=No              |
| **FeatureModel**             | R=Sí / W=Sí (global)                  | R=Sí / W=Sí (solo propios)                          | R=Sí / W=Sí (solo donde colabora; sin crear ni borrar) | R=Sí / W=No                                           | R=Sí (publicados) / W=No                         | R=Sí (publicados) / W=No |
| **FeatureModelVersion**      | R=Sí / W=Sí (global)                  | R=Sí / W=Sí (propios; puede llevar DRAFT→IN_REVIEW) | R=Sí / W=Sí (permitidos; no puede llevar a IN_REVIEW)  | R=Sí / W=Sí (solo transición de revisión/publicación) | R=No especificado / W=No especificado            | R=No / W=No              |
| **Feature**                  | R=Sí / W=Sí (global)                  | R=Sí / W=Sí (en sus modelos)                        | R=Sí / W=Sí (en modelos permitidos)                    | R=Sí / W=No                                           | R=No especificado / W=No especificado            | R=No / W=No              |
| **FeatureRelation**          | R=Sí / W=Sí (global)                  | R=Sí / W=Sí (en sus modelos)                        | R=Sí / W=Sí (en modelos permitidos)                    | R=Sí / W=No                                           | R=No especificado / W=No especificado            | R=No / W=No              |
| **FeatureGroup**             | R=Sí / W=Sí (global)                  | R=Sí / W=Sí (en sus modelos)                        | R=Sí / W=Sí (en modelos permitidos)                    | R=Sí / W=No                                           | R=No especificado / W=No especificado            | R=No / W=No              |
| **Constraint**               | R=Sí / W=Sí (global)                  | R=Sí / W=Sí (en sus modelos)                        | R=Sí / W=Sí (en modelos permitidos)                    | R=Sí / W=No                                           | R=No especificado / W=No especificado            | R=No / W=No              |
| **FeatureModelCollaborator** | R=No especificado / W=No especificado | R=Sí / W=Sí (gestiona colaboradores de sus modelos) | R=Sí / W=No                                            | R=No / W=No                                           | R=No / W=No                                      | R=No / W=No              |
| **Resource / Tag**           | R=Sí / W=Sí (global)                  | R=Sí / W=Sí                                         | R=Sí / W=Sí                                            | R=No especificado / W=No especificado                 | R=Sí / W=Sí (acotado según configuración propia) | R=No / W=No              |
| **Configuration**            | R=Sí / W=Sí (global)                  | R=Sí / W=No                                         | R=No especificado / W=No especificado                  | R=No / W=No                                           | R=Sí / W=Sí (propias)                            | R=Sí (públicas) / W=No   |

---

## 4.3 Lectura ejecutiva del modelo de seguridad por rol

- **ADMIN:** gobierno completo de plataforma y datos.
- **MODEL_DESIGNER:** propietario funcional del ciclo de diseño del modelo.
- **MODEL_EDITOR:** colaborador con capacidad de edición acotada al ámbito invitado.
- **REVIEWER:** rol de control de calidad y publicación, sin edición estructural.
- **CONFIGURATOR:** consumidor experto de modelos publicados para derivar configuraciones.
- **VIEWER:** acceso de solo lectura a artefactos finales/publicados.

---

## 5) Hallazgos de consistencia y recomendaciones

1. El sistema implementa correctamente separación entre **edición**, **revisión** y **consumo** de modelos.
2. Hay buen desacople operativo por asincronía para cargas pesadas.
3. Existen entidades donde algunos permisos no están totalmente explícitos en el documento inicial (marcados como **No especificado**).
4. Recomendación: consolidar una **matriz única de autorización ejecutable** (fuente de verdad) para eliminar ambigüedad entre documentación y código.
5. Recomendación XP: convertir esta matriz en pruebas de autorización por rol (TDD de permisos).

---

## 6) Conclusión

El backend ofrece una plataforma amplia y madura para gestión de feature models, con ciclo de vida completo (diseño, validación, publicación, configuración, análisis y exportación), y un esquema RBAC alineado con responsabilidades reales de negocio.

El principal punto de mejora es cerrar completamente los casos “No especificado” en una política formal, versionada y testeada de permisos.
