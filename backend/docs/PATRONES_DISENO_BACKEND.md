# Patrones de diseño modernos en el backend (además de GRASP)

> Alcance: patrones observables en modelos, servicios, repositorios y dependencias del backend.

---

## Clasificación (GoF vs GRASP)

**GoF**

- **Creacionales**
  - `Singleton`: [backend/app/core/redis.py](backend/app/core/redis.py), [backend/app/core/cache.py](backend/app/core/cache.py), [backend/app/core/s3.py](backend/app/core/s3.py), [backend/app/core/config.py](backend/app/core/config.py)
  - `Factory Method`: [backend/app/core/redis.py](backend/app/core/redis.py), [backend/app/core/cache.py](backend/app/core/cache.py), [backend/app/core/logging.py](backend/app/core/logging.py), [backend/app/core/config.py](backend/app/core/config.py)

- **Estructurales**
- `Facade`: [backend/app/services/feature_model/fm_analysis_facade.py](backend/app/services/feature_model/fm_analysis_facade.py)
- `Builder`: [backend/app/services/feature_model/fm_tree_builder.py](backend/app/services/feature_model/fm_tree_builder.py)
- `Decorator`: [backend/app/api/v1/routes/feature_model.py](backend/app/api/v1/routes/feature_model.py), [backend/app/tasks/feature_model_analysis.py](backend/app/tasks/feature_model_analysis.py)
- `Strategy`: [backend/app/services/feature_model/fm_configuration_generator.py](backend/app/services/feature_model/fm_configuration_generator.py), [backend/app/services/feature_model/fm_logical_validator.py](backend/app/services/feature_model/fm_logical_validator.py)
- `Chain of Responsibility`: [backend/app/middlewares/common.py](backend/app/middlewares/common.py)
- `Observer`: [backend/app/core/celery.py](backend/app/core/celery.py)
- `Adapter`: [backend/app/core/s3.py](backend/app/core/s3.py)
- `Proxy` (protección): [backend/app/core/security.py](backend/app/core/security.py), [backend/app/api/deps.py](backend/app/api/deps.py)

- **Comportamiento**
- `Command`: [backend/app/tasks/feature_model_analysis.py](backend/app/tasks/feature_model_analysis.py), [backend/app/tasks/maintenance.py](backend/app/tasks/maintenance.py)
- `State`: [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py)

**GRASP**

- `Repository` → _Pure Fabrication_ + _Indirection_ (reduce acoplamiento con persistencia): [backend/app/repositories/base.py](backend/app/repositories/base.py)
- `Service Layer` → _Pure Fabrication_ (centraliza lógica de negocio): [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py)
- `Controller` (orquestación de casos de uso en API): [backend/app/api/v1/routes/feature_model.py](backend/app/api/v1/routes/feature_model.py), [backend/app/api/v1/routes/domain.py](backend/app/api/v1/routes/domain.py)
- `Low Coupling / Indirection` (inyección de dependencias): [backend/app/api/deps.py](backend/app/api/deps.py)

**Nota:** `DTO`, `Dependency Injection`, `Cache‑Aside`, `Copy‑on‑Write`, `Task/Work Queue`, `Object Pool`, `Unit of Work`, `Middleware Pipeline` y `Retry with Backoff` son patrones arquitectónicos/infraestructura (no GoF/GRASP), pero se mantienen documentados por su relevancia técnica.

---

## Cobertura por tipos/subtipos (mínimo 2)

| Tipo            | Subtipo                         | Patrones detectados                                                                                                        |
| --------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| GoF             | Creacionales                    | `Singleton`, `Factory Method`                                                                                              |
| GoF             | Estructurales                   | `Adapter`, `Facade`, `Decorator`, `Proxy`                                                                                  |
| GoF             | Comportamiento                  | `Strategy`, `Command`, `Observer`, `Chain of Responsibility`, `State`                                                      |
| GRASP           | Asignación de responsabilidades | `Controller`, `Pure Fabrication`, `Indirection`, `Low Coupling`                                                            |
| Arquitectónicos | Persistencia/Infra              | `Repository`, `Unit of Work`, `Object Pool`, `Cache-Aside`, `Task/Work Queue`, `Middleware Pipeline`, `Retry with Backoff` |

---

## 1) Repository (GRASP)

**Qué es:** Aísla el acceso a datos detrás de una interfaz/repositorio, separando persistencia de lógica de negocio.

**Evidencia:**

- Repositorios concretos y base: [backend/app/repositories/base.py](backend/app/repositories/base.py), [backend/app/repositories/feature_model.py](backend/app/repositories/feature_model.py), [backend/app/repositories/feature.py](backend/app/repositories/feature.py), [backend/app/repositories/feature_model_version.py](backend/app/repositories/feature_model_version.py).
- Inyección de repositorios via dependencias: [backend/app/api/deps.py](backend/app/api/deps.py).

---

## 2) Service Layer (GRASP)

**Qué es:** Encapsula lógica de negocio en servicios de aplicación, evitando que los controladores (routers) conozcan detalles de dominio/persistencia.

**Evidencia:**

- Servicios de Feature Model y settings: [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py), [backend/app/services/feature_model/fm_export.py](backend/app/services/feature_model/fm_export.py), [backend/app/services/feature_model/fm_uvl_importer.py](backend/app/services/feature_model/fm_uvl_importer.py), [backend/app/services/settings.py](backend/app/services/settings.py).

---

## 3) Facade (GoF)

**Qué es:** Provee una API de alto nivel que orquesta varios subsistemas para simplificar el uso.

**Evidencia:**

- Facade de análisis que compone validación lógica, análisis estructural y UVL: [backend/app/services/feature_model/fm_analysis_facade.py](backend/app/services/feature_model/fm_analysis_facade.py).

---

## 4) Builder (GoF)

**Qué es:** Construye paso a paso una estructura compleja (árbol completo del FM), separando construcción de representación.

**Evidencia:**

- Constructor del árbol completo para respuesta: [backend/app/services/feature_model/fm_tree_builder.py](backend/app/services/feature_model/fm_tree_builder.py).

---

## 5) Strategy (GoF)

**Qué es:** Encapsula algoritmos intercambiables bajo una misma interfaz, eligiéndose en tiempo de ejecución.

**Evidencia:**

- Generación/optimización de configuraciones con estrategias: [backend/app/services/feature_model/fm_configuration_generator.py](backend/app/services/feature_model/fm_configuration_generator.py).
- Validación lógica multi‑motor (sympy/pysat/z3) como estrategia interna: [backend/app/services/feature_model/fm_logical_validator.py](backend/app/services/feature_model/fm_logical_validator.py).

---

## 6) Data Transfer Object (DTO) (Arquitectónico)

**Qué es:** Objetos de transporte que definen contratos de entrada/salida en la API (evitan exponer entidades directamente).

**Evidencia:**

- Esquemas de dominio y API: [backend/app/models/feature_model.py](backend/app/models/feature_model.py), [backend/app/models/feature.py](backend/app/models/feature.py), [backend/app/models/domain.py](backend/app/models/domain.py), [backend/app/models/user.py](backend/app/models/user.py).

---

## 7) Dependency Injection (DI) (Arquitectónico)

**Qué es:** Inversión de control para resolver dependencias (repositorios, sesión) desde el framework.

**Evidencia:**

- Dependencias con `Depends()` y repositorios inyectados: [backend/app/api/deps.py](backend/app/api/deps.py).

---

## 8) Cache‑Aside (Arquitectónico)

**Qué es:** El servicio consulta caché primero y, si no existe, recupera de la base y guarda en caché.

**Evidencia:**

- `SettingsService` leyendo de Redis y luego DB: [backend/app/services/settings.py](backend/app/services/settings.py).

---

## 9) Copy‑on‑Write (variación de versionado) (Arquitectónico)

**Qué es:** Los cambios crean una nueva versión clonando la anterior, preservando historial (útil en dominio de versionado).

**Evidencia:**

- Creación de versiones y clonación en repositorios y manager: [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py), [backend/app/repositories/feature_model_version.py](backend/app/repositories/feature_model_version.py), [backend/app/repositories/feature.py](backend/app/repositories/feature.py).

---

## 10) Chain of Responsibility (GoF)

**Qué es:** Encadena handlers que procesan una petición de forma secuencial, donde cada eslabón puede actuar o delegar.

**Evidencia:**

- Cadena de middlewares para operaciones de escritura y caché: [backend/app/middlewares/common.py](backend/app/middlewares/common.py).

---

## 11) Observer (GoF)

**Qué es:** Un sujeto notifica eventos a observadores registrados (callbacks) sin acoplamiento directo.

**Evidencia:**

- Señales de Celery para init/shutdown de workers: [backend/app/core/celery.py](backend/app/core/celery.py).

---

## 12) Singleton (GoF)

**Qué es:** Controla una única instancia compartida para acceso global.

**Evidencia:**

- Instancias compartidas: `redis_client`, `cache_service`, `minio_client`: [backend/app/core/redis.py](backend/app/core/redis.py), [backend/app/core/cache.py](backend/app/core/cache.py), [backend/app/core/s3.py](backend/app/core/s3.py).

---

## 13) Adapter (GoF)

**Qué es:** Envuelve una API externa para exponer una interfaz propia y estable.

**Evidencia:**

- `MinIOClient` como wrapper del SDK MinIO: [backend/app/core/s3.py](backend/app/core/s3.py).

---

## 14) Task / Work Queue (Arquitectónico)

**Qué es:** Desacopla trabajo pesado en tareas asíncronas y colas de procesamiento.

**Evidencia:**

- Celery + colas + tareas de análisis: [backend/app/core/celery.py](backend/app/core/celery.py), [backend/app/tasks/feature_model_analysis.py](backend/app/tasks/feature_model_analysis.py).

---

## 15) Command (GoF)

**Qué es:** Encapsula una petición como objeto/función ejecutable, permitiendo encolar, reintentar y monitorear su ejecución.

**Evidencia:**

- Tareas Celery como comandos de ejecución diferida: [backend/app/tasks/feature_model_analysis.py](backend/app/tasks/feature_model_analysis.py), [backend/app/tasks/maintenance.py](backend/app/tasks/maintenance.py).

---

## 16) Object Pool (Arquitectónico)

**Qué es:** Reutiliza objetos costosos (conexiones) a través de un pool compartido.

**Evidencia:**

- Pools Redis para caché y requests: [backend/app/core/redis.py](backend/app/core/redis.py), pools separados en cache: [backend/app/core/cache.py](backend/app/core/cache.py).

---

## 17) Factory Method (GoF - Creacional)

**Qué es:** Delega la creación de objetos a métodos/factories especializados para desacoplar construcción de uso.

**Evidencia:**

- Fábricas de pools/instancias: `_build_pool(...)` y constructores auxiliares en [backend/app/core/redis.py](backend/app/core/redis.py), [backend/app/core/cache.py](backend/app/core/cache.py), factory de logger en [backend/app/core/logging.py](backend/app/core/logging.py), fábrica cacheada de settings en [backend/app/core/config.py](backend/app/core/config.py).

---

## 18) Decorator (GoF - Estructural)

**Qué es:** Añade comportamiento a funciones/métodos sin modificar su implementación base.

**Evidencia:**

- Decoradores de caché y ruteo: `@cache`, `@router.get/post/patch` en [backend/app/api/v1/routes/feature_model.py](backend/app/api/v1/routes/feature_model.py), [backend/app/api/v1/routes/domain.py](backend/app/api/v1/routes/domain.py).
- Decoradores de tareas/registro en Celery: `@celery_app.task` en [backend/app/tasks/feature_model_analysis.py](backend/app/tasks/feature_model_analysis.py).

---

## 19) State (GoF - Comportamiento)

**Qué es:** El comportamiento/acciones válidas dependen del estado actual del objeto.

**Evidencia:**

- Transiciones de estado de versiones (`DRAFT` → `PUBLISHED` → `ARCHIVED` → `PUBLISHED`) y validaciones de transición en [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py).

---

## 20) Proxy (GoF - Estructural, protección)

**Qué es:** Interpone un objeto/componente para controlar acceso al recurso real.

**Evidencia:**

- Guardas de seguridad (`require_api_key`, `require_admin_key`) y dependencias de autorización en [backend/app/core/security.py](backend/app/core/security.py), [backend/app/api/deps.py](backend/app/api/deps.py).

---

## 21) Unit of Work (Arquitectónico)

**Qué es:** Agrupa cambios en una transacción y define fronteras de commit/rollback.

**Evidencia:**

- Uso sistemático de `AsyncSession` + `commit/refresh` en repositorios: [backend/app/repositories/domain.py](backend/app/repositories/domain.py), [backend/app/repositories/user.py](backend/app/repositories/user.py), [backend/app/repositories/feature_model.py](backend/app/repositories/feature_model.py).

---

## 22) Middleware Pipeline (Arquitectónico)

**Qué es:** La petición pasa por una cadena ordenada de middleware antes/después del handler.

**Evidencia:**

- Configuración del pipeline en app y middleware de invalidación de caché: [backend/app/main.py](backend/app/main.py), [backend/app/middlewares/common.py](backend/app/middlewares/common.py).

---

## 23) Retry with Backoff (Arquitectónico de resiliencia)

**Qué es:** Reintenta operaciones fallidas con espera exponencial para reducir fallas transitorias.

**Evidencia:**

- Configuración de `Retry(ExponentialBackoff(...))` en pools Redis: [backend/app/core/redis.py](backend/app/core/redis.py), [backend/app/core/cache.py](backend/app/core/cache.py).

---

Si quieres, agrego patrones adicionales (por ejemplo, _Specification_, _Adapter_ o _CQRS_ si aplican) o trazo cada patrón con RF/historias específicas.
