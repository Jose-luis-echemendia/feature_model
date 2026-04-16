# Patrones de diseño modernos en el backend (además de GRASP)

> Alcance: patrones observables en modelos, servicios, repositorios y dependencias del backend.

---

## 1) Repository

**Qué es:** Aísla el acceso a datos detrás de una interfaz/repositorio, separando persistencia de lógica de negocio.

**Evidencia:**

- Repositorios concretos y base: [backend/app/repositories/base.py](backend/app/repositories/base.py), [backend/app/repositories/feature_model.py](backend/app/repositories/feature_model.py), [backend/app/repositories/feature.py](backend/app/repositories/feature.py), [backend/app/repositories/feature_model_version.py](backend/app/repositories/feature_model_version.py).
- Inyección de repositorios via dependencias: [backend/app/api/deps.py](backend/app/api/deps.py).

---

## 2) Service Layer

**Qué es:** Encapsula lógica de negocio en servicios de aplicación, evitando que los controladores (routers) conozcan detalles de dominio/persistencia.

**Evidencia:**

- Servicios de Feature Model y settings: [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py), [backend/app/services/feature_model/fm_export.py](backend/app/services/feature_model/fm_export.py), [backend/app/services/feature_model/fm_uvl_importer.py](backend/app/services/feature_model/fm_uvl_importer.py), [backend/app/services/settings.py](backend/app/services/settings.py).

---

## 3) Facade

**Qué es:** Provee una API de alto nivel que orquesta varios subsistemas para simplificar el uso.

**Evidencia:**

- Facade de análisis que compone validación lógica, análisis estructural y UVL: [backend/app/services/feature_model/fm_analysis_facade.py](backend/app/services/feature_model/fm_analysis_facade.py).

---

## 4) Builder

**Qué es:** Construye paso a paso una estructura compleja (árbol completo del FM), separando construcción de representación.

**Evidencia:**

- Constructor del árbol completo para respuesta: [backend/app/services/feature_model/fm_tree_builder.py](backend/app/services/feature_model/fm_tree_builder.py).

---

## 5) Strategy

**Qué es:** Encapsula algoritmos intercambiables bajo una misma interfaz, eligiéndose en tiempo de ejecución.

**Evidencia:**

- Generación/optimización de configuraciones con estrategias: [backend/app/services/feature_model/fm_configuration_generator.py](backend/app/services/feature_model/fm_configuration_generator.py).
- Validación lógica multi‑motor (sympy/pysat/z3) como estrategia interna: [backend/app/services/feature_model/fm_logical_validator.py](backend/app/services/feature_model/fm_logical_validator.py).

---

## 6) Data Transfer Object (DTO)

**Qué es:** Objetos de transporte que definen contratos de entrada/salida en la API (evitan exponer entidades directamente).

**Evidencia:**

- Esquemas de dominio y API: [backend/app/models/feature_model.py](backend/app/models/feature_model.py), [backend/app/models/feature.py](backend/app/models/feature.py), [backend/app/models/domain.py](backend/app/models/domain.py), [backend/app/models/user.py](backend/app/models/user.py).

---

## 7) Dependency Injection (DI)

**Qué es:** Inversión de control para resolver dependencias (repositorios, sesión) desde el framework.

**Evidencia:**

- Dependencias con `Depends()` y repositorios inyectados: [backend/app/api/deps.py](backend/app/api/deps.py).

---

## 8) Cache‑Aside

**Qué es:** El servicio consulta caché primero y, si no existe, recupera de la base y guarda en caché.

**Evidencia:**

- `SettingsService` leyendo de Redis y luego DB: [backend/app/services/settings.py](backend/app/services/settings.py).

---

## 9) Copy‑on‑Write (variación de versionado)

**Qué es:** Los cambios crean una nueva versión clonando la anterior, preservando historial (útil en dominio de versionado).

**Evidencia:**

- Creación de versiones y clonación en repositorios y manager: [backend/app/services/feature_model/fm_version_manager.py](backend/app/services/feature_model/fm_version_manager.py), [backend/app/repositories/feature_model_version.py](backend/app/repositories/feature_model_version.py), [backend/app/repositories/feature.py](backend/app/repositories/feature.py).

---

Si quieres, agrego patrones adicionales (por ejemplo, _Specification_, _Adapter_ o _CQRS_ si aplican) o trazo cada patrón con RF/historias específicas.
