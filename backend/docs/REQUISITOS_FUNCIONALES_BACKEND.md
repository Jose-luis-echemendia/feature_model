# Requisitos Funcionales Implementados en el Backend

Fecha de análisis: 2026-04-08

## Metodología aplicada

### Pasada 1 (levantamiento funcional)

- Revisión de routers registrados en `backend/app/api/v1/router.py`.
- Revisión de endpoints en `backend/app/api/v1/routes/*.py`.
- Revisión de documentación técnica en `backend/docs` para contextualizar capacidades.

### Pasada 2 (cobertura y control de omisiones)

- Extracción automática de endpoints por AST para confirmar cobertura total.
- Conteo resultante: **127 endpoints funcionales** (incluye `websocket`).
- Verificación de presencia por cada archivo de rutas.

---

## Tabla de requisitos funcionales implementados

| No. | Nombre                                          | Descripción                                                                                                                                        | Prioridad | Complejidad |
| --: | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ----------- |
|   1 | Health check de vida                            | Permite verificar que el proceso backend está activo (`GET /health-check`).                                                                        | Alta      | Baja        |
|   2 | Estado detallado del sistema                    | Entrega estado de PostgreSQL, Redis, Celery, MinIO y métricas del host (`GET /status`).                                                            | Alta      | Media       |
|   3 | Login con token JWT                             | Autentica usuario por email/contraseña y emite `access_token` (`POST /login/access-token`).                                                        | Alta      | Media       |
|   4 | Verificación de token actual                    | Valida token y devuelve usuario autenticado (`POST /login/test-token`).                                                                            | Alta      | Baja        |
|   5 | Solicitud de recuperación de contraseña         | Genera y envía token de recuperación por email (`POST /password-recovery/{email}`).                                                                | Alta      | Media       |
|   6 | Restablecimiento de contraseña                  | Permite cambiar contraseña con token de recuperación (`POST /reset-password`).                                                                     | Alta      | Media       |
|   7 | Preview HTML de correo de recuperación          | Devuelve contenido HTML del correo de recuperación para administración (`POST /password-recovery-html-content/{email}`).                           | Media     | Baja        |
|   8 | Listado de usuarios                             | Lista usuarios con paginación para roles autorizados (`GET /users`).                                                                               | Alta      | Baja        |
|   9 | Listado de usuarios por rol                     | Filtra usuarios por rol con paginación (`GET /users/by-role/{role}`).                                                                              | Media     | Baja        |
|  10 | Creación de usuarios                            | Crea usuarios según reglas de rol y permisos (`POST /users`).                                                                                      | Alta      | Media       |
|  11 | Actualización de perfil propio                  | Permite al usuario actualizar sus datos personales (`PATCH /users/me`).                                                                            | Alta      | Baja        |
|  12 | Cambio de contraseña propia                     | Permite al usuario autenticado cambiar su contraseña (`PATCH /users/me/password`).                                                                 | Alta      | Baja        |
|  13 | Consulta de perfil propio                       | Devuelve datos del usuario autenticado (`GET /users/me`).                                                                                          | Media     | Baja        |
|  14 | Eliminación de cuenta propia                    | Permite eliminar la cuenta propia con restricciones (`DELETE /users/me`).                                                                          | Media     | Baja        |
|  15 | Registro público de usuario                     | Permite alta de usuario cuando el sistema lo habilita (`POST /users/signup`).                                                                      | Alta      | Media       |
|  16 | Consulta de usuario por ID                      | Obtiene datos de un usuario específico con control de permisos (`GET /users/{user_id}`).                                                           | Media     | Baja        |
|  17 | Actualización de usuario por ID                 | Permite a superusuario actualizar usuario (`PATCH /users/{user_id}`).                                                                              | Alta      | Baja        |
|  18 | Cambio de rol de usuario                        | Permite modificar rol de un usuario (`PUT /users/{user_id}/role`).                                                                                 | Alta      | Baja        |
|  19 | Eliminación de usuario por ID                   | Permite eliminar usuario por administración (`DELETE /users/{user_id}`).                                                                           | Alta      | Baja        |
|  20 | Búsqueda de usuarios                            | Busca usuarios por término (`GET /users/search/{search_term}`).                                                                                    | Media     | Baja        |
|  21 | Activación de usuario                           | Activa usuario inactivo (`PATCH /users/{user_id}/activate`).                                                                                       | Media     | Baja        |
|  22 | Desactivación de usuario                        | Desactiva usuario activo (`PATCH /users/{user_id}/deactivate`).                                                                                    | Media     | Baja        |
|  23 | Listado de dominios                             | Lista dominios con manejo de visibilidad por rol (`GET /domains`).                                                                                 | Alta      | Baja        |
|  24 | Consulta de dominio por ID                      | Obtiene detalle de dominio (`GET /domains/{domain_id}`).                                                                                           | Media     | Baja        |
|  25 | Creación de dominio                             | Crea nuevo dominio (admin) (`POST /domains`).                                                                                                      | Alta      | Baja        |
|  26 | Actualización de dominio                        | Actualiza datos de dominio (`PATCH /domains/{domain_id}`).                                                                                         | Alta      | Baja        |
|  27 | Eliminación de dominio                          | Elimina dominio si no tiene dependencias (`DELETE /domains/{domain_id}`).                                                                          | Alta      | Media       |
|  28 | Búsqueda de dominios                            | Busca dominios por nombre o descripción (`GET /domains/search`).                                                                                   | Media     | Baja        |
|  29 | Dominio con feature models                      | Consulta dominio incluyendo feature models asociados (`GET /domains/{domain_id}/with-feature-models`).                                             | Media     | Baja        |
|  30 | Activación de dominio                           | Activa dominio (`PATCH /domains/{domain_id}/activate`).                                                                                            | Media     | Baja        |
|  31 | Desactivación de dominio                        | Desactiva dominio (`PATCH /domains/{domain_id}/deactivate`).                                                                                       | Media     | Baja        |
|  32 | Listado de feature models                       | Lista feature models con paginación y filtro por dominio (`GET /feature-models`).                                                                  | Alta      | Media       |
|  33 | Creación de feature model                       | Crea feature model en dominio válido (`POST /feature-models`).                                                                                     | Alta      | Media       |
|  34 | Consulta de feature model                       | Obtiene detalle de feature model con versiones (`GET /feature-models/{model_id}`).                                                                 | Alta      | Media       |
|  35 | Actualización de feature model                  | Actualiza metadata del feature model (`PATCH /feature-models/{model_id}`).                                                                         | Alta      | Media       |
|  36 | Activación de feature model                     | Activa feature model (`PATCH /feature-models/{model_id}/activate`).                                                                                | Alta      | Baja        |
|  37 | Desactivación de feature model                  | Desactiva feature model (`PATCH /feature-models/{model_id}/deactivate`).                                                                           | Alta      | Baja        |
|  38 | Eliminación de feature model                    | Elimina feature model validando que no tenga dependencias (`DELETE /feature-models/{model_id}`).                                                   | Alta      | Media       |
|  39 | Listado de versiones de modelo                  | Lista versiones de un feature model (`GET /feature-models/{model_id}/versions`).                                                                   | Alta      | Baja        |
|  40 | Consulta de versión específica                  | Obtiene versión concreta de feature model (`GET /feature-models/{model_id}/versions/{version_id}`).                                                | Alta      | Baja        |
|  41 | Creación de versión                             | Crea nueva versión (copy-on-write opcional desde fuente) (`POST /feature-models/{model_id}/versions`).                                             | Alta      | Media       |
|  42 | Publicación de versión                          | Publica versión y ejecuta validaciones asociadas (`PATCH /feature-models/{model_id}/versions/{version_id}/publish`).                               | Alta      | Alta        |
|  43 | Archivado de versión                            | Cambia estado de versión a archivada (`PATCH /feature-models/{model_id}/versions/{version_id}/archive`).                                           | Media     | Baja        |
|  44 | Restauración de versión                         | Restaura versión archivada (`PATCH /feature-models/{model_id}/versions/{version_id}/restore`).                                                     | Media     | Baja        |
|  45 | Estructura completa de última versión publicada | Devuelve árbol completo de la última versión publicada (`GET /feature-models/{model_id}/versions/latest/complete`).                                | Alta      | Alta        |
|  46 | Estructura completa por versión                 | Devuelve árbol completo por `version_id` (`GET /feature-models/{model_id}/versions/{version_id}/complete`).                                        | Alta      | Alta        |
|  47 | Estadísticas de última versión publicada        | Obtiene métricas de versión publicada más reciente (`GET /feature-models/{model_id}/versions/latest/statistics`).                                  | Alta      | Media       |
|  48 | Estadísticas por versión                        | Obtiene métricas de complejidad/estructura por versión (`GET /feature-models/{model_id}/versions/{version_id}/statistics`).                        | Alta      | Media       |
|  49 | Estadísticas en tiempo real por WebSocket       | Streaming de estadísticas de versión vía WebSocket (`WS /ws/feature-models/{model_id}/versions/{version_id}/statistics`).                          | Alta      | Alta        |
|  50 | Consulta de conexiones WS activas               | Permite auditar conexiones activas por versión (`GET /ws/feature-models/versions/{version_id}/connections`).                                       | Media     | Media       |
|  51 | Exportación de última versión publicada         | Exporta última versión en formato solicitado (`GET /feature-models/{model_id}/versions/latest/export/{format}`).                                   | Alta      | Media       |
|  52 | Exportación de versión específica               | Exporta versión en formato solicitado (`GET /feature-models/{model_id}/versions/{version_id}/export/{format}`).                                    | Alta      | Media       |
|  53 | Obtención UVL efectivo                          | Devuelve UVL almacenado o generado desde estructura (`GET /feature-models/{model_id}/versions/{version_id}/uvl`).                                  | Alta      | Media       |
|  54 | Guardado de UVL                                 | Persiste UVL validado y dispara análisis asíncrono (`PUT /feature-models/{model_id}/versions/{version_id}/uvl`).                                   | Alta      | Alta        |
|  55 | Sincronización UVL desde estructura             | Regenera y guarda UVL desde modelo visual (`POST /feature-models/{model_id}/versions/{version_id}/uvl/sync-from-structure`).                       | Alta      | Alta        |
|  56 | Aplicar UVL a estructura                        | Crea nueva versión estructural desde UVL (`POST /feature-models/{model_id}/versions/{version_id}/uvl/apply-to-structure`).                         | Alta      | Alta        |
|  57 | Diff UVL vs estructura actual                   | Devuelve diferencias antes de aplicar cambios UVL (`POST /feature-models/{model_id}/versions/{version_id}/uvl/diff`).                              | Alta      | Alta        |
|  58 | Validación lógica del modelo                    | Evalúa satisfacibilidad/consistencia lógica global (`POST /feature-models/{model_id}/versions/{version_id}/validation/model`).                     | Alta      | Alta        |
|  59 | Validación estructural del modelo               | Valida raíz, ciclos y huérfanos (`POST /feature-models/{model_id}/versions/{version_id}/validation/structure`).                                    | Alta      | Media       |
|  60 | Validación de configuración seleccionada        | Verifica selección concreta de features (`POST /feature-models/{model_id}/versions/{version_id}/validation/configuration`).                        | Alta      | Alta        |
|  61 | Análisis estructural de validación              | Ejecuta análisis de dead features, redundancias, SCC, etc. (`POST /feature-models/{model_id}/versions/{version_id}/validation/analysis`).          | Alta      | Alta        |
|  62 | Validación integral full                        | Ejecuta validación lógica + estructura + análisis en una sola operación (`POST /feature-models/{model_id}/versions/{version_id}/validation/full`). | Alta      | Alta        |
|  63 | Resumen de análisis síncrono                    | Genera resumen avanzado de análisis para una versión (`POST /feature-models/{model_id}/versions/{version_id}/analysis/summary`).                   | Alta      | Alta        |
|  64 | Comparación síncrona entre versiones            | Compara dos versiones con delta de resultados (`POST /feature-models/{model_id}/versions/{version_id}/analysis/compare`).                          | Alta      | Alta        |
|  65 | Lanzamiento de análisis batch                   | Inicia análisis asíncrono en Celery (`POST /feature-models/{model_id}/versions/{version_id}/analysis/batch`).                                      | Alta      | Alta        |
|  66 | Generación masiva asíncrona                     | Lanza generación masiva de configuraciones (`POST /feature-models/{model_id}/versions/{version_id}/analysis/batch/bulk-configurations`).           | Alta      | Alta        |
|  67 | Export bundle asíncrono                         | Lanza exportación en lote de formatos (`POST /feature-models/{model_id}/versions/{version_id}/analysis/batch/export-bundle`).                      | Media     | Alta        |
|  68 | Comparación batch asíncrona                     | Lanza comparación de versiones en background (`POST /feature-models/{model_id}/versions/{version_id}/analysis/batch/compare`).                     | Media     | Alta        |
|  69 | Recomputación de estadísticas batch             | Recalcula estadísticas de versión en background (`POST /feature-models/{model_id}/versions/{version_id}/analysis/batch/recompute-stats`).          | Media     | Media       |
|  70 | Estado de tarea de análisis                     | Consulta estado/resultados de tareas de análisis (`GET /feature-models/analysis/tasks/{task_id}`).                                                 | Alta      | Baja        |
|  71 | Estado genérico de tarea                        | Consulta estado y resultado de cualquier task Celery (`GET /tasks/{task_id}`).                                                                     | Media     | Baja        |
|  72 | Cancelación de tarea                            | Revoca tarea en cola o en ejecución (`POST /tasks/{task_id}/cancel`).                                                                              | Media     | Baja        |
|  73 | Consulta de progreso de tarea                   | Obtiene progreso incremental reportado por la tarea (`GET /tasks/{task_id}/progress`).                                                             | Media     | Baja        |
|  74 | Crear configuración persistente                 | Crea configuración asociada a una versión validando consistencia (`POST /configurations`).                                                         | Alta      | Alta        |
|  75 | Consultar configuración por ID                  | Obtiene configuración con features relacionados (`GET /configurations/{id}`).                                                                      | Media     | Baja        |
|  76 | Listar configuraciones                          | Lista configuraciones con paginación (`GET /configurations`).                                                                                      | Media     | Baja        |
|  77 | Actualizar configuración                        | Modifica metadatos/features de configuración (`PUT /configurations/{id}`).                                                                         | Media     | Baja        |
|  78 | Eliminar configuración                          | Elimina configuración (`DELETE /configurations/{id}`).                                                                                             | Media     | Baja        |
|  79 | Validar configuración propuesta                 | Valida selección de features sin persistir (`POST /configurations/validate`).                                                                      | Alta      | Alta        |
|  80 | Generar configuraciones válidas                 | Genera una o múltiples configuraciones según estrategia (`POST /configurations/generate`).                                                         | Alta      | Alta        |
|  81 | Optimizar configuraciones                       | Ejecuta generación optimizada (NSGA2/CP-SAT/BDD) (`POST /configurations/optimize`).                                                                | Alta      | Alta        |
|  82 | Opciones de configuración por etapas            | Calcula can/must select/deselect según selección parcial (`POST /configurations/staged/options`).                                                  | Alta      | Alta        |
|  83 | Listado de features                             | Lista features con filtros y/o árbol por versión (`GET /features`).                                                                                | Alta      | Media       |
|  84 | Creación de feature                             | Crea feature en versión aplicando permisos y validaciones (`POST /features`).                                                                      | Alta      | Alta        |
|  85 | Consulta de feature por ID                      | Obtiene detalle de feature (`GET /features/{feature_id}`).                                                                                         | Media     | Baja        |
|  86 | Consulta de subárbol de feature                 | Devuelve feature con descendencia (`GET /features/{feature_id}/children`).                                                                         | Media     | Media       |
|  87 | Consulta de relaciones de feature               | Lista relaciones donde participa una feature (`GET /features/{feature_id}/relations`).                                                             | Media     | Baja        |
|  88 | Listado de tags de feature                      | Lista tags asociados a una feature (`GET /features/{feature_id}/tags`).                                                                            | Media     | Baja        |
|  89 | Asociación tag-feature                          | Asocia un tag a una feature (`POST /features/{feature_id}/tags/{tag_id}`).                                                                         | Media     | Baja        |
|  90 | Desasociación tag-feature                       | Elimina asociación de tag con feature (`DELETE /features/{feature_id}/tags/{tag_id}`).                                                             | Media     | Baja        |
|  91 | Actualización parcial de feature                | Actualiza campos de feature con copy-on-write (`PATCH /features/{feature_id}`).                                                                    | Alta      | Alta        |
|  92 | Reemplazo completo de feature                   | Reemplaza campos principales de feature (`PUT /features/{feature_id}`).                                                                            | Alta      | Alta        |
|  93 | Movimiento de feature                           | Reubica feature cambiando parent (`PATCH /features/{feature_id}/move`).                                                                            | Alta      | Alta        |
|  94 | Eliminación de feature                          | Elimina feature creando nueva versión (`DELETE /features/{feature_id}`).                                                                           | Alta      | Alta        |
|  95 | Listado de feature groups                       | Lista grupos con filtros por versión/padre/tipo (`GET /feature-groups`).                                                                           | Media     | Baja        |
|  96 | Consulta de feature group                       | Obtiene grupo por ID (`GET /feature-groups/{group_id}`).                                                                                           | Media     | Baja        |
|  97 | Creación de feature group                       | Crea grupo con copy-on-write y validaciones (`POST /feature-groups`).                                                                              | Alta      | Alta        |
|  98 | Actualización de feature group                  | Actualiza grupo con copy-on-write (`PATCH /feature-groups/{group_id}`).                                                                            | Alta      | Alta        |
|  99 | Reemplazo de feature group                      | Reemplaza grupo completo (`PUT /feature-groups/{group_id}`).                                                                                       | Alta      | Alta        |
| 100 | Eliminación de feature group                    | Elimina grupo con copy-on-write (`DELETE /feature-groups/{group_id}`).                                                                             | Alta      | Alta        |
| 101 | Listado de feature relations                    | Lista relaciones con filtros (`GET /feature-relations`).                                                                                           | Media     | Baja        |
| 102 | Consulta de feature relation                    | Obtiene relación por ID (`GET /feature-relations/{relation_id}`).                                                                                  | Media     | Baja        |
| 103 | Creación de feature relation                    | Crea relación con copy-on-write (`POST /feature-relations`).                                                                                       | Alta      | Alta        |
| 104 | Actualización de feature relation               | Actualiza relación (`PATCH /feature-relations/{relation_id}`).                                                                                     | Alta      | Alta        |
| 105 | Reemplazo de feature relation                   | Reemplaza relación completa (`PUT /feature-relations/{relation_id}`).                                                                              | Alta      | Alta        |
| 106 | Eliminación de feature relation                 | Elimina relación con copy-on-write (`DELETE /feature-relations/{relation_id}`).                                                                    | Alta      | Alta        |
| 107 | Listado de constraints                          | Lista constraints por filtros (`GET /constraints`).                                                                                                | Media     | Baja        |
| 108 | Consulta de constraint                          | Obtiene constraint por ID (`GET /constraints/{constraint_id}`).                                                                                    | Media     | Baja        |
| 109 | Creación de constraint                          | Crea constraint compleja con copy-on-write (`POST /constraints`).                                                                                  | Alta      | Alta        |
| 110 | Actualización de constraint                     | Actualiza constraint (`PATCH /constraints/{constraint_id}`).                                                                                       | Alta      | Alta        |
| 111 | Reemplazo de constraint                         | Reemplaza constraint (`PUT /constraints/{constraint_id}`).                                                                                         | Alta      | Alta        |
| 112 | Eliminación de constraint                       | Elimina constraint con copy-on-write (`DELETE /constraints/{constraint_id}`).                                                                      | Alta      | Alta        |
| 113 | Listado de tags                                 | Lista tags activas (`GET /tags`).                                                                                                                  | Media     | Baja        |
| 114 | Consulta de tag                                 | Obtiene tag por ID (`GET /tags/{tag_id}`).                                                                                                         | Media     | Baja        |
| 115 | Creación de tag                                 | Crea tag con nombre único (`POST /tags`).                                                                                                          | Media     | Baja        |
| 116 | Listado de recursos                             | Lista recursos con paginación (`GET /resources`).                                                                                                  | Media     | Baja        |
| 117 | Consulta de recurso                             | Obtiene recurso por ID (`GET /resources/{resource_id}`).                                                                                           | Media     | Baja        |
| 118 | Creación de recurso                             | Crea recurso (asignando owner cuando aplica) (`POST /resources`).                                                                                  | Media     | Baja        |
| 119 | Actualización de recurso                        | Actualiza recurso y valida permisos de ownership (`PATCH /resources/{resource_id}`).                                                               | Media     | Media       |
| 120 | Guía de acceso a documentación interna          | Entrega instrucciones para autenticarse en docs internas (`GET /utils/docs-access`).                                                               | Baja      | Baja        |
| 121 | Endpoint de prueba de error interno             | Simula error inesperado para pruebas de manejadores (`GET /utils/test/internal-error`).                                                            | Baja      | Baja        |
| 122 | Envío de email de prueba                        | Permite probar mecanismo de envío de correo (`POST /utils/test-email`).                                                                            | Baja      | Baja        |
| 123 | Lectura dinámica de setting de ejemplo          | Verifica lectura de settings dinámicas (`GET /utils/test/setting`).                                                                                | Baja      | Baja        |
| 124 | Catálogo de roles del sistema                   | Devuelve roles disponibles (`GET /utils/roles`).                                                                                                   | Baja      | Baja        |
| 125 | Catálogo de enums para frontend                 | Devuelve opciones de enums para formularios (`GET /utils/options`).                                                                                | Media     | Baja        |
| 126 | Limpieza de caché                               | Elimina claves de caché Redis por patrones (`POST /utils/clear-cache`).                                                                            | Media     | Media       |
| 127 | Creación privada de usuario                     | Crea usuario por ruta privada/local (`POST /private/users`).                                                                                       | Baja      | Baja        |

---

## Capacidades transversales registradas desde `core`, `middlewares` y `services`

Estas capacidades sí se registran porque generan comportamiento observable o soportan flujos funcionales del backend. No se incluyen aquí elementos puramente técnicos como conexión a BD, logging interno, bootstrap de Celery o utilidades sin efecto funcional visible.

| No. | Nombre                                         | Descripción                                                                                                                                                      | Prioridad | Complejidad |
| --: | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ----------- |
| 128 | Configuración dinámica de la aplicación        | Permite leer valores dinámicos como `ALLOWS_USER_REGISTRATION`, `MAINTENANCE_MODE` e `ITEMS_PER_PAGE` para modificar el comportamiento del sistema sin redeploy. | Alta      | Media       |
| 129 | Gestión persistente de settings                | Permite consultar, actualizar y cachear configuraciones de aplicación mediante `SettingsService`, con persistencia en BD y Redis.                                | Alta      | Media       |
| 130 | Invalidación automática de caché en escrituras | Invalida caché asociada cuando ocurre una escritura exitosa sobre rutas de configuración, evitando datos obsoletos.                                              | Media     | Baja        |
| 131 | Gestión de estado de jobs internos             | Persiste y consulta estado/progreso de jobs de validación, importación, análisis y tareas genéricas para polling del frontend.                                   | Alta      | Media       |
| 132 | Control de almacenamiento de recursos          | Gestiona buckets de MinIO al arranque y soporta carga, descarga firmada y eliminación de recursos asociados a features.                                          | Alta      | Alta        |
| 133 | Gestión de artefactos exportables              | Genera objetos de exportación y facilita su descarga temporal mediante URLs presignadas para formatos de salida.                                                 | Alta      | Media       |

---

## Segunda pasada de cobertura (control de omisiones)

### Conteo automático por archivo de rutas (AST)

- `configuration.py`: 9
- `constraint.py`: 6
- `domain.py`: 9
- `feature.py`: 12
- `feature_group.py`: 6
- `feature_model.py`: 7
- `feature_model_analysis.py`: 8
- `feature_model_complete.py`: 2
- `feature_model_export.py`: 2
- `feature_model_statistics.py`: 2
- `feature_model_statistics_ws.py`: 2
- `feature_model_uvl.py`: 5
- `feature_model_validation.py`: 5
- `feature_model_version.py`: 6
- `feature_relation.py`: 6
- `health.py`: 2
- `login.py`: 5
- `private.py`: 1
- `resources.py`: 4
- `tags.py`: 3
- `tasks.py`: 3
- `user.py`: 15
- `utils.py`: 7

**Total validado:** **127 endpoints funcionales**

### Resultado de cobertura

- Requisitos registrados en tabla: **127**
- Endpoints detectados automáticamente: **127**
- Cobertura declarada: **100% (127/127)**

### Capacidades transversales adicionales registradas

- Ítems añadidos desde `core`/`middlewares`/`services`: **6**
- Total de capacidades documentadas en el archivo: **133**

### Nota de alcance

Este inventario cubre **requisitos funcionales implementados y expuestos por el backend** (API REST/WS + operaciones funcionales de soporte observables).
