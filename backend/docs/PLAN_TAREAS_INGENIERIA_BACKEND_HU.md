# Plan de tareas de ingeniería (Backend) alineado a RF y HU

## Alcance

Este plan define tareas técnicas para implementar las historias de usuario del backend del sistema de modelos de características, incluyendo controladores, servicios, repositorios, esquemas, modelos, excepciones y tareas asíncronas.

## Convenciones

- **HU-01..HU-14**: numeración usada en este plan para las historias descritas.
- **Programador responsable**: Jose Luis Echemendia López.
- **Fechas**: planificación base propuesta (ajustable por sprint).

## Mapeo HU

- **HU-01**: Autenticación y Autogestión de cuenta
- **HU-02**: Administración de Usuarios y Permisos
- **HU-03**: Gestión de Dominios de Conocimiento
- **HU-04**: Gestión Operativa de FM
- **HU-05**: Gestión de Versiones y Publicación
- **HU-06**: Análisis de Métricas y Exportación
- **HU-07**: Edición de la Jerarquía de Características
- **HU-08**: Modelado de Grupos y Relaciones Estructurales
- **HU-09**: Gestión de Restricciones Transversales
- **HU-10**: Integración y Sincronización UVL
- **HU-11**: Validación Lógica y Estructural del Modelo
- **HU-12**: Gestión de Configuraciones
- **HU-13**: Validación y Generación Automática de Configuraciones
- **HU-14**: Enriquecimiento con Recursos y Taxonomías

---

## Tareas de ingeniería

| Nº tarea | Nº HU | Nombre de la tarea                             | Tipo de tarea                                           | Tiempo estimado | Fecha inicio | Fecha fin  | Programador responsable    | Descripción                                                                                                                           |
| -------- | ----- | ---------------------------------------------- | ------------------------------------------------------- | --------------: | ------------ | ---------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| T-001    | HU-01 | Diseñar modelo de token de recuperación        | Definir modelos                                         |              6h | 2026-04-20   | 2026-04-20 | Jose Luis Echemendia López | Definir entidad para recuperación de contraseña (token, expiración, estado, usuario), con auditoría y compatibilidad de persistencia. |
| T-002    | HU-01 | Implementar esquemas de autenticación          | Crear esquemas de validación entrada de la api y salida |              8h | 2026-04-20   | 2026-04-21 | Jose Luis Echemendia López | Crear DTOs para registro, login, solicitud de recuperación, restablecimiento (token y autenticado), y actualización de perfil propio. |
| T-003    | HU-01 | Implementar servicio de autenticación y cuenta | Crear servicio                                          |             12h | 2026-04-21   | 2026-04-22 | Jose Luis Echemendia López | Implementar lógica de registro, login, hash de contraseñas, emisión/validación de tokens y actualización de perfil.                   |
| T-004    | HU-01 | Exponer endpoints de auth y perfil             | Crear controlador                                       |             10h | 2026-04-22   | 2026-04-23 | Jose Luis Echemendia López | Crear rutas para RF#1, RF#2, RF#3, RF#4, RF#5 y RF#8 con validaciones, permisos y respuestas estandarizadas.                          |
| T-005    | HU-01 | Enviar correos de recuperación asíncronamente  | Crear tareas de celery                                  |              6h | 2026-04-23   | 2026-04-24 | Jose Luis Echemendia López | Implementar tarea asíncrona para envío de token de recuperación, reintentos, plantillas y trazabilidad.                               |

| T-006 | HU-02 | Implementar esquemas para gestión de usuarios | Crear esquemas de validación entrada de la api y salida | 6h | 2026-04-27 | 2026-04-27 | Jose Luis Echemendia López | Definir esquemas de listado paginado, filtros por rol/término, cambio de rol y activación/desactivación de cuenta. |
| T-007 | HU-02 | Implementar repositorio administrativo de usuarios | Crear repositorio | 8h | 2026-04-27 | 2026-04-28 | Jose Luis Echemendia López | Añadir consultas de listado, filtrado, búsqueda, cambios de rol y cambio de estado activo/inactivo con soft delete lógico. |
| T-008 | HU-02 | Implementar servicio de administración de usuarios | Crear servicio | 10h | 2026-04-28 | 2026-04-29 | Jose Luis Echemendia López | Orquestar reglas de negocio de permisos, transición de roles y validaciones de seguridad para administración de cuentas. |
| T-009 | HU-02 | Exponer endpoints de administración de usuarios | Crear controlador | 8h | 2026-04-29 | 2026-04-30 | Jose Luis Echemendia López | Crear rutas de RF#6, RF#7, RF#9, RF#10 y RF#11 con guardas de autorización por rol administrativo. |
| T-010 | HU-02 | Definir excepciones de administración de usuarios | Crear excepciones personalizadas | 4h | 2026-04-30 | 2026-04-30 | Jose Luis Echemendia López | Definir errores de transición inválida de rol, usuario no encontrado y operación no permitida. |

| T-011 | HU-03 | Ajustar modelo de dominio curricular | Definir modelos | 6h | 2026-05-04 | 2026-05-04 | Jose Luis Echemendia López | Validar campos de Domain (nombre único, descripción, estado activo), auditoría y relación con modelos. |
| T-012 | HU-03 | Implementar esquemas de dominio | Crear esquemas de validación entrada de la api y salida | 6h | 2026-05-04 | 2026-05-05 | Jose Luis Echemendia López | Crear schemas para crear, actualizar, listar, buscar y obtener dominio con modelos asociados. |
| T-013 | HU-03 | Implementar repositorio de dominios | Crear repositorio | 8h | 2026-05-05 | 2026-05-06 | Jose Luis Echemendia López | Implementar consultas paginadas, filtros de búsqueda y obtención de dominio con relaciones. |
| T-014 | HU-03 | Implementar servicio de gobernanza de dominios | Crear servicio | 8h | 2026-05-06 | 2026-05-07 | Jose Luis Echemendia López | Aplicar reglas de negocio para activación/desactivación y control de integridad del dominio. |
| T-015 | HU-03 | Exponer endpoints de dominios | Crear controlador | 8h | 2026-05-07 | 2026-05-08 | Jose Luis Echemendia López | Implementar rutas RF#12 a RF#19 con validaciones y respuestas consistentes. |

| T-016 | HU-04 | Ajustar modelo de FeatureModel y colaboradores | Definir modelos | 8h | 2026-05-11 | 2026-05-11 | Jose Luis Echemendia López | Consolidar entidad de FM, vínculo a dominio, propietario y colaboradores con reglas de unicidad. |
| T-017 | HU-04 | Implementar esquemas operativos de FM | Crear esquemas de validación entrada de la api y salida | 8h | 2026-05-11 | 2026-05-12 | Jose Luis Echemendia López | Definir payloads de creación, actualización, listado paginado y detalle de FM con metadatos. |
| T-018 | HU-04 | Implementar repositorio de FM | Crear repositorio | 8h | 2026-05-12 | 2026-05-13 | Jose Luis Echemendia López | Implementar persistencia y consultas por dominio, estado y búsqueda de modelos. |
| T-019 | HU-04 | Implementar servicio operativo de FM | Crear servicio | 10h | 2026-05-13 | 2026-05-14 | Jose Luis Echemendia López | Gestionar creación, actualización, activación/desactivación e integridad de datos del catálogo de FM. |
| T-020 | HU-04 | Exponer endpoints de ciclo operativo de FM | Crear controlador | 8h | 2026-05-14 | 2026-05-15 | Jose Luis Echemendia López | Publicar rutas RF#20 a RF#25 con filtros, paginación y control de acceso por rol. |

| T-021 | HU-05 | Ajustar modelo de versionado de FM | Definir modelos | 8h | 2026-05-18 | 2026-05-18 | Jose Luis Echemendia López | Definir estados de versión (draft/published/archived), metadata de snapshot y campos de trazabilidad. |
| T-022 | HU-05 | Implementar repositorio de versiones | Crear repositorio | 10h | 2026-05-18 | 2026-05-19 | Jose Luis Echemendia López | Crear consultas de versiones por FM, versión publicada más reciente y carga de versión específica. |
| T-023 | HU-05 | Implementar gestor de versionado copy-on-write | Crear clase | 14h | 2026-05-19 | 2026-05-21 | Jose Luis Echemendia López | Crear clase FeatureModelVersionManager para crear versión, publicar, archivar y restaurar con validaciones de transición. |
| T-024 | HU-05 | Exponer endpoints de versiones y publicación | Crear controlador | 10h | 2026-05-21 | 2026-05-22 | Jose Luis Echemendia López | Implementar RF#26, RF#27, RF#28, RF#29, RF#30, RF#31 y RF#32 con control de permisos y consistencia. |
| T-025 | HU-05 | Definir excepciones de transición de versiones | Crear excepciones personalizadas | 4h | 2026-05-22 | 2026-05-22 | Jose Luis Echemendia López | Crear excepciones para transición inválida, versión no publicable y conflictos de estado. |

| T-026 | HU-06 | Implementar servicio de exportación multiformato | Crear servicio | 16h | 2026-05-25 | 2026-05-26 | Jose Luis Echemendia López | Implementar FeatureModelExportService para UVL, XML, TVL, DIMACS, JSON, DOT y Mermaid con mapeo UUID↔int. |
| T-027 | HU-06 | Implementar esquemas de métricas y exportación | Crear esquemas de validación entrada de la api y salida | 6h | 2026-05-26 | 2026-05-26 | Jose Luis Echemendia López | Definir request/response para estadísticas y exportación por versión o versión publicada. |
| T-028 | HU-06 | Exponer endpoints de estadísticas y exportación | Crear controlador | 8h | 2026-05-26 | 2026-05-27 | Jose Luis Echemendia López | Crear rutas RF#33 y RF#34 con negociación de formato, streaming o descarga de archivo. |
| T-029 | HU-06 | Implementar tareas asíncronas de exportación | Crear tareas de celery | 8h | 2026-05-27 | 2026-05-28 | Jose Luis Echemendia López | Delegar exportaciones pesadas en Celery y guardar artefactos en almacenamiento de objetos con estado de proceso. |
| T-030 | HU-06 | Definir excepciones de exportación | Crear excepciones personalizadas | 4h | 2026-05-28 | 2026-05-28 | Jose Luis Echemendia López | Gestionar formato no soportado, versión no encontrada y fallo de serialización/exportación. |

| T-031 | HU-07 | Ajustar modelo de Feature para edición jerárquica | Definir modelos | 8h | 2026-06-01 | 2026-06-01 | Jose Luis Echemendia López | Revisar entidad Feature (padre, hijos, grupo, recurso, propiedades, estado activo) con integridad referencial. |
| T-032 | HU-07 | Implementar esquemas de jerarquía de features | Crear esquemas de validación entrada de la api y salida | 8h | 2026-06-01 | 2026-06-02 | Jose Luis Echemendia López | Definir payloads para crear, actualizar, mover, obtener detalle/subárbol y activar/desactivar feature. |
| T-033 | HU-07 | Implementar repositorio de features | Crear repositorio | 10h | 2026-06-02 | 2026-06-03 | Jose Luis Echemendia López | Añadir operaciones de recorrido jerárquico, búsqueda por versión, actualización parcial y soft delete lógico. |
| T-034 | HU-07 | Implementar servicio de jerarquía de features | Crear servicio | 12h | 2026-06-03 | 2026-06-04 | Jose Luis Echemendia López | Aplicar reglas de consistencia al mover nodos y ejecutar copy-on-write al activar/desactivar. |
| T-035 | HU-07 | Exponer endpoints de features estructurales | Crear controlador | 8h | 2026-06-04 | 2026-06-05 | Jose Luis Echemendia López | Implementar RF#53, RF#54, RF#55, RF#56, RF#60, RF#61, RF#62 y RF#63 con validaciones de permisos. |

| T-036 | HU-08 | Ajustar modelos de FeatureGroup y FeatureRelation | Definir modelos | 8h | 2026-06-08 | 2026-06-08 | Jose Luis Echemendia López | Definir entidades de grupos y relaciones (tipos, cardinalidades, origen/destino, estado) y reglas de integridad. |
| T-037 | HU-08 | Implementar esquemas de grupos y relaciones | Crear esquemas de validación entrada de la api y salida | 8h | 2026-06-08 | 2026-06-09 | Jose Luis Echemendia López | Crear esquemas para listar, crear, actualizar, activar/desactivar grupos y relaciones. |
| T-038 | HU-08 | Implementar repositorios de grupos y relaciones | Crear repositorio | 10h | 2026-06-09 | 2026-06-10 | Jose Luis Echemendia López | Implementar consultas por versión, feature padre y tipo de agrupación/relación. |
| T-039 | HU-08 | Implementar servicio de semántica estructural | Crear servicio | 12h | 2026-06-10 | 2026-06-11 | Jose Luis Echemendia López | Validar cardinalidades, consistencia de relaciones cross-tree y copy-on-write al modificar estructura. |
| T-040 | HU-08 | Exponer endpoints de grupos y relaciones | Crear controlador | 8h | 2026-06-11 | 2026-06-12 | Jose Luis Echemendia López | Implementar RF#64 a RF#75 con validación semántica y autorización. |

| T-041 | HU-09 | Ajustar modelo de restricciones lógicas | Definir modelos | 6h | 2026-06-15 | 2026-06-15 | Jose Luis Echemendia López | Definir entidad Constraint con expresión textual y normalizada (CNF), estado y metadatos de versión. |
| T-042 | HU-09 | Implementar esquemas de restricciones | Crear esquemas de validación entrada de la api y salida | 6h | 2026-06-15 | 2026-06-16 | Jose Luis Echemendia López | Definir payloads para listar, obtener, crear, actualizar, activar y desactivar restricciones. |
| T-043 | HU-09 | Implementar repositorio de restricciones | Crear repositorio | 8h | 2026-06-16 | 2026-06-17 | Jose Luis Echemendia López | Crear consultas por versión, estado y búsqueda de restricciones con paginación. |
| T-044 | HU-09 | Implementar servicio de restricciones transversales | Crear servicio | 12h | 2026-06-17 | 2026-06-18 | Jose Luis Echemendia López | Validar sintaxis, transformar expresiones y preservar versionado al editar/activar/desactivar. |
| T-045 | HU-09 | Exponer endpoints de restricciones | Crear controlador | 8h | 2026-06-18 | 2026-06-19 | Jose Luis Echemendia López | Implementar RF#76 a RF#81 y manejo homogéneo de errores de lógica. |

| T-046 | HU-10 | Implementar importador UVL a estructura | Crear clase | 14h | 2026-06-22 | 2026-06-23 | Jose Luis Echemendia López | Implementar FeatureModelUVLImporter para parsear, validar y construir estructura interna desde UVL. |
| T-047 | HU-10 | Implementar esquemas de sincronización UVL | Crear esquemas de validación entrada de la api y salida | 6h | 2026-06-23 | 2026-06-23 | Jose Luis Echemendia López | Definir esquemas para guardar UVL, sincronizar UVL desde estructura y aplicar UVL a estructura. |
| T-048 | HU-10 | Implementar servicio de sincronización UVL | Crear servicio | 12h | 2026-06-23 | 2026-06-24 | Jose Luis Echemendia López | Orquestar equivalencia modelo visual/textual, persistencia de UVL efectivo y creación de nuevas versiones. |
| T-049 | HU-10 | Exponer endpoints de integración UVL | Crear controlador | 8h | 2026-06-24 | 2026-06-25 | Jose Luis Echemendia López | Implementar RF#36, RF#37, RF#38 y RF#39 con validaciones previas y mensajes de error claros. |
| T-050 | HU-10 | Definir excepciones de UVL | Crear excepciones personalizadas | 4h | 2026-06-25 | 2026-06-26 | Jose Luis Echemendia López | Crear excepciones para UVL inválido, divergencia de sincronización y conflicto de estructura. |

| T-051 | HU-11 | Implementar validador lógico SAT/SMT | Crear clase | 16h | 2026-06-29 | 2026-06-30 | Jose Luis Echemendia López | Implementar FeatureModelLogicalValidator para consistencia global y validación de configuraciones propuestas. |
| T-052 | HU-11 | Implementar analizador estructural | Crear clase | 12h | 2026-06-30 | 2026-07-01 | Jose Luis Echemendia López | Implementar análisis de ciclos, huérfanos, dead features, redundancias y SCC. |
| T-053 | HU-11 | Implementar fachada de análisis del FM | Crear servicio | 10h | 2026-07-01 | 2026-07-02 | Jose Luis Echemendia López | Orquestar validación lógica y estructural en FeatureModelAnalysisFacade con respuestas agregadas. |
| T-054 | HU-11 | Implementar esquemas de respuesta de análisis | Crear esquemas de validación entrada de la api y salida | 6h | 2026-07-02 | 2026-07-02 | Jose Luis Echemendia López | Definir contratos API para reportes de satisfacibilidad, inconsistencias y hallazgos estructurales. |
| T-055 | HU-11 | Exponer endpoints de validación y análisis | Crear controlador | 8h | 2026-07-02 | 2026-07-03 | Jose Luis Echemendia López | Implementar RF#39, RF#40, RF#41 y RF#42 con ejecución segura y timeout configurable. |

| T-056 | HU-12 | Ajustar modelo de Configuration | Definir modelos | 8h | 2026-07-06 | 2026-07-06 | Jose Luis Echemendia López | Definir entidad Configuration con relación a versión y features seleccionadas, estado activo e historial. |
| T-057 | HU-12 | Implementar esquemas de configuraciones persistentes | Crear esquemas de validación entrada de la api y salida | 8h | 2026-07-06 | 2026-07-07 | Jose Luis Echemendia López | Crear DTOs para crear, obtener, listar, actualizar, activar/desactivar y validar selección propuesta. |
| T-058 | HU-12 | Implementar repositorio de configuraciones | Crear repositorio | 8h | 2026-07-07 | 2026-07-08 | Jose Luis Echemendia López | Implementar persistencia paginada, filtros por versión/estado y carga de relaciones con features. |
| T-059 | HU-12 | Implementar servicio de gestión de configuraciones | Crear servicio | 12h | 2026-07-08 | 2026-07-09 | Jose Luis Echemendia López | Validar consistencia, persistir configuraciones y aplicar reglas de activación/desactivación. |
| T-060 | HU-12 | Exponer endpoints de configuraciones | Crear controlador | 8h | 2026-07-09 | 2026-07-10 | Jose Luis Echemendia López | Implementar RF#44, RF#45, RF#46, RF#47, RF#48 y RF#49 en API v1. |

| T-061 | HU-13 | Implementar generador de configuraciones válidas | Crear clase | 14h | 2026-07-13 | 2026-07-14 | Jose Luis Echemendia López | Implementar FeatureModelConfigurationGenerator con estrategias GREEDY, RANDOM y BEAM para RF#50. |
| T-062 | HU-13 | Implementar optimización de configuraciones | Crear servicio | 14h | 2026-07-14 | 2026-07-15 | Jose Luis Echemendia López | Integrar estrategias GENETIC/NSGA2 y criterios de calidad para RF#51. |
| T-063 | HU-13 | Implementar esquemas de generación/optimización | Crear esquemas de validación entrada de la api y salida | 6h | 2026-07-15 | 2026-07-15 | Jose Luis Echemendia López | Definir contratos de entrada/salida para validación propuesta, generación y optimización de configuraciones. |
| T-064 | HU-13 | Exponer endpoints de validación y generación automática | Crear controlador | 8h | 2026-07-15 | 2026-07-16 | Jose Luis Echemendia López | Implementar RF#49, RF#50, RF#51 y RF#52 en rutas de configuración avanzada. |
| T-065 | HU-13 | Ejecutar optimización intensiva en background | Crear tareas de celery | 8h | 2026-07-16 | 2026-07-17 | Jose Luis Echemendia López | Delegar ejecuciones pesadas de optimización a Celery con persistencia de estado y resultados parciales/finales. |

| T-066 | HU-14 | Ajustar modelos de Tag y Resource | Definir modelos | 10h | 2026-07-20 | 2026-07-21 | Jose Luis Echemendia López | Definir entidades Tag y Resource con unicidad, metadatos extendidos y enlaces a feature/owner. |
| T-067 | HU-14 | Implementar esquemas de etiquetas y recursos | Crear esquemas de validación entrada de la api y salida | 8h | 2026-07-21 | 2026-07-21 | Jose Luis Echemendia López | Definir payloads para CRUD de tags, CRUD parcial de resources y asociación/desasociación de tags en features. |
| T-068 | HU-14 | Implementar repositorios de taxonomías y recursos | Crear repositorio | 10h | 2026-07-21 | 2026-07-22 | Jose Luis Echemendia López | Implementar búsquedas paginadas, filtros y operaciones de vínculo entre entidades. |
| T-069 | HU-14 | Implementar servicio de enriquecimiento semántico | Crear servicio | 12h | 2026-07-22 | 2026-07-23 | Jose Luis Echemendia López | Aplicar reglas de negocio de propietario, versionado de metadatos y consistencia de asociaciones tag-feature-resource. |
| T-070 | HU-14 | Exponer endpoints de tags y recursos | Crear controlador | 8h | 2026-07-23 | 2026-07-24 | Jose Luis Echemendia López | Implementar RF#57, RF#58, RF#59, RF#82, RF#83, RF#84, RF#85, RF#86, RF#87 y RF#88. |

---

## Notas técnicas de ejecución

- Implementar en módulos de `backend/app/api`, `backend/app/services`, `backend/app/repositories`, `backend/app/schemas`, `backend/app/models` y `backend/app/tasks`.
- Mantener soft delete y auditoría en entidades sensibles.
- Aplicar control de acceso por rol en routers.
- Para tareas de alto costo computacional, usar Celery y persistir estado de proceso.
- Validar contratos con pruebas unitarias e integración por HU.
