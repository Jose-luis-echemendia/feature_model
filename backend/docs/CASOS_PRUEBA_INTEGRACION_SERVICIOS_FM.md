# Casos de Prueba de Integración - Controladores de Servicios FM

## Alcance

Estos casos están orientados a pruebas de integración API (controlador + servicio + repositorio + BD, y cuando aplique cola/asíncrono) para los controladores de servicios de Feature Model (FM).

> Base URL asumida: `/api/v1`

---

## HU4: Gestión Operativa de FM

### Caso de Prueba: INT_FM_CTRL_001

| Campo                        | Valor                                                                                                                                                                                                                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID de prueba**             | INT_FM_CTRL_001                                                                                                                                                                                                                                                                                  |
| **HU**                       | HU4 - Gestión Operativa de FM                                                                                                                                                                                                                                                                    |
| **Nombre**                   | Crear feature model en dominio válido                                                                                                                                                                                                                                                            |
| **Descripción**              | Verificar que `POST /feature-models/` crea un FM y persiste metadatos correctamente.                                                                                                                                                                                                             |
| **Condiciones de ejecución** | - Backend arriba<br>- BD limpia o controlada<br>- Usuario autenticado con rol `MODEL_DESIGNER` o `ADMIN`<br>- Existe `domain_id` activo                                                                                                                                                          |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-models/` con `name`, `description`, `domain_id`.<br>2. Validar HTTP 201.<br>3. Verificar respuesta con `id`, `owner_id`, `domain_id`, `is_active=true`.<br>4. Consultar `GET /api/v1/feature-models/{id}`.<br>5. Confirmar persistencia en BD (registro creado). |
| **Resultado esperada**       | - Se crea el FM correctamente.<br>- El `owner_id` corresponde al usuario autenticado.<br>- Se registra `created_at`/`updated_at`.                                                                                                                                                                |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia: request/response + query BD).                                                                                                                                                                                                                              |

### Caso de Prueba: INT_FM_CTRL_002

| Campo                        | Valor                                                                                                                                                      |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_002                                                                                                                                            |
| **HU**                       | HU4 - Gestión Operativa de FM                                                                                                                              |
| **Nombre**                   | Crear FM con dominio inexistente                                                                                                                           |
| **Descripción**              | Verificar manejo de error de negocio cuando `domain_id` no existe.                                                                                         |
| **Condiciones de ejecución** | - Usuario autenticado con permisos de diseño<br>- `domain_id` inexistente                                                                                  |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-models/` con `domain_id` inválido.<br>2. Validar respuesta de error.<br>3. Verificar que no se crea ningún registro en BD. |
| **Resultado esperada**       | - HTTP 404 (o error de dominio equivalente).<br>- Mensaje claro de dominio no encontrado.<br>- Sin efectos colaterales en BD.                              |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                     |

---

## HU5: Gestión de Versiones y Publicación

### Caso de Prueba: INT_FM_CTRL_003

| Campo                        | Valor                                                                                                                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID de prueba**             | INT_FM_CTRL_003                                                                                                                                                                                                                      |
| **HU**                       | HU5 - Gestión de Versiones y Publicación                                                                                                                                                                                             |
| **Nombre**                   | Crear nueva versión COW desde versión origen                                                                                                                                                                                         |
| **Descripción**              | Verificar que `POST /feature-models/{model_id}/versions` crea nueva versión por copy-on-write.                                                                                                                                       |
| **Condiciones de ejecución** | - Existe FM con versión origen<br>- Usuario propietario del FM o superusuario                                                                                                                                                        |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-models/{model_id}/versions` con `source_version_id`.<br>2. Validar respuesta exitosa.<br>3. Verificar que `version_number` se incrementa.<br>4. Confirmar que la versión origen permanece inmutable. |
| **Resultado esperada**       | - HTTP 200/201 según contrato actual.<br>- Nueva versión creada en estado editable.<br>- Estructura clonada sin modificar versión fuente.                                                                                            |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                               |

### Caso de Prueba: INT_FM_CTRL_004

| Campo                        | Valor                                                                                                                                                                                                     |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_004                                                                                                                                                                                           |
| **HU**                       | HU5 - Gestión de Versiones y Publicación                                                                                                                                                                  |
| **Nombre**                   | Publicar versión válida                                                                                                                                                                                   |
| **Descripción**              | Verificar que `PATCH /feature-models/{model_id}/versions/{version_id}/publish` cambia estado y persiste publicación.                                                                                      |
| **Condiciones de ejecución** | - Versión existente y publicable<br>- Usuario propietario o superusuario                                                                                                                                  |
| **Pasos de ejecución**       | 1. Ejecutar `PATCH /api/v1/feature-models/{model_id}/versions/{version_id}/publish`.<br>2. Validar respuesta.<br>3. Consultar versión por `GET`.<br>4. Verificar estado final y timestamp de publicación. |
| **Resultado esperada**       | - Estado pasa a `PUBLISHED`.<br>- Se guarda `published_at` (si aplica).<br>- Integridad de datos preservada.                                                                                              |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                    |

---

## HU7: Edición de Jerarquía de Features

### Caso de Prueba: INT_FM_CTRL_005

| Campo                        | Valor                                                                                                                                                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_005                                                                                                                                                                                                        |
| **HU**                       | HU7 - Edición de la Jerarquía de Características                                                                                                                                                                       |
| **Nombre**                   | Crear feature en versión de FM                                                                                                                                                                                         |
| **Descripción**              | Verificar que `POST /features/` crea feature y respeta validaciones de parent/version.                                                                                                                                 |
| **Condiciones de ejecución** | - Existe versión destino<br>- Usuario con rol `MODEL_DESIGNER`/`ADMIN`/`DEVELOPER`                                                                                                                                     |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/features/` con `feature_model_version_id`, `name`, `type`.<br>2. Validar HTTP 201.<br>3. Consultar `GET /api/v1/features/{feature_id}`.<br>4. Validar persistencia y pertenencia a la versión. |
| **Resultado esperada**       | - Feature creada con ID único.<br>- Datos consistentes en BD.<br>- Sin corrupción del árbol.                                                                                                                           |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                 |

### Caso de Prueba: INT_FM_CTRL_006

| Campo                        | Valor                                                                                                                                                |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_006                                                                                                                                      |
| **HU**                       | HU7 - Edición de la Jerarquía de Características                                                                                                     |
| **Nombre**                   | Reubicar feature con padre inválido                                                                                                                  |
| **Descripción**              | Verificar rechazo de `PATCH /features/{feature_id}/move` cuando el nuevo padre no pertenece a la misma versión.                                      |
| **Condiciones de ejecución** | - Feature origen existente<br>- `parent_id` de otra versión o inexistente                                                                            |
| **Pasos de ejecución**       | 1. Enviar `PATCH /api/v1/features/{feature_id}/move` con `parent_id` inválido.<br>2. Verificar código de error.<br>3. Consultar la feature original. |
| **Resultado esperada**       | - HTTP 400.<br>- Mensaje de inconsistencia de padre.<br>- Estructura original se mantiene intacta.                                                   |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                               |

---

## HU8: Grupos y Relaciones Estructurales

### Caso de Prueba: INT_FM_CTRL_007

| Campo                        | Valor                                                                                                                                                                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_007                                                                                                                                                                                                                                       |
| **HU**                       | HU8 - Modelado de Grupos y Relaciones Estructurales                                                                                                                                                                                                   |
| **Nombre**                   | Crear grupo OR con cardinalidades válidas                                                                                                                                                                                                             |
| **Descripción**              | Verificar integración de `POST /feature-groups/` con reglas de cardinalidad y versionado COW.                                                                                                                                                         |
| **Condiciones de ejecución** | - Feature padre existente<br>- Usuario propietario del modelo o superusuario                                                                                                                                                                          |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-groups/` con `group_type=OR`, `min_cardinality`, `max_cardinality`, `parent_feature_id`.<br>2. Validar HTTP 201.<br>3. Consultar grupo creado.<br>4. Verificar nueva versión derivada del modelo (si aplica por COW). |
| **Resultado esperada**       | - Grupo creado correctamente.<br>- Cardinalidades persistidas.<br>- Nueva versión consistente del modelo.                                                                                                                                             |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                |

### Caso de Prueba: INT_FM_CTRL_008

| Campo                        | Valor                                                                                                                                                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID de prueba**             | INT_FM_CTRL_008                                                                                                                                                                                                                |
| **HU**                       | HU8 - Modelado de Grupos y Relaciones Estructurales                                                                                                                                                                            |
| **Nombre**                   | Crear relación EXCLUDES válida                                                                                                                                                                                                 |
| **Descripción**              | Verificar que `POST /feature-relations/` crea relación cross-tree y la persiste.                                                                                                                                               |
| **Condiciones de ejecución** | - Features source/target existentes en misma versión<br>- Usuario con permisos                                                                                                                                                 |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-relations/` con `type=EXCLUDES`.<br>2. Validar HTTP 201.<br>3. Consultar `GET /api/v1/feature-relations/{relation_id}`.<br>4. Verificar que la relación queda activa y vinculada a la versión. |
| **Resultado esperada**       | - Relación creada y consistente.<br>- IDs de source/target correctos.<br>- Registro trazable en BD.                                                                                                                            |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                         |

---

## HU9: Restricciones Transversales

### Caso de Prueba: INT_FM_CTRL_009

| Campo                        | Valor                                                                                                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_009                                                                                                                                                   |
| **HU**                       | HU9 - Gestión de Restricciones Transversales                                                                                                                      |
| **Nombre**                   | Crear constraint con expresión válida                                                                                                                             |
| **Descripción**              | Verificar que `POST /constraints/` integra validación y persistencia de restricciones.                                                                            |
| **Condiciones de ejecución** | - Versión de FM existente<br>- Usuario dueño o superusuario                                                                                                       |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/constraints/` con `expr_text` válido.<br>2. Validar HTTP 201.<br>3. Leer constraint por ID.<br>4. Confirmar persistencia y estado activo. |
| **Resultado esperada**       | - Constraint creada correctamente.<br>- Se mantiene consistencia del modelo/versionado COW.                                                                       |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                            |

### Caso de Prueba: INT_FM_CTRL_010

| Campo                        | Valor                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID de prueba**             | INT_FM_CTRL_010                                                                                                                            |
| **HU**                       | HU9 - Gestión de Restricciones Transversales                                                                                               |
| **Nombre**                   | Crear constraint con sintaxis inválida                                                                                                     |
| **Descripción**              | Verificar control de errores al intentar persistir una restricción inválida.                                                               |
| **Condiciones de ejecución** | - Versión existente<br>- Usuario con permisos                                                                                              |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/constraints/` con `expr_text` inválido.<br>2. Validar respuesta de error.<br>3. Confirmar que no se crea registro. |
| **Resultado esperada**       | - HTTP 400.<br>- Mensaje de validación semántica/sintáctica.<br>- BD sin nuevos constraints inválidos.                                     |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                     |

---

## HU10: Integración y Sincronización UVL

### Caso de Prueba: INT_FM_CTRL_011

| Campo                        | Valor                                                                                                                                                                                                                                                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_011                                                                                                                                                                                                                                                                                                   |
| **HU**                       | HU10 - Integración y Sincronización UVL                                                                                                                                                                                                                                                                           |
| **Nombre**                   | Guardar UVL y disparar análisis asíncrono                                                                                                                                                                                                                                                                         |
| **Descripción**              | Verificar que `PUT /feature-models/{model_id}/versions/{version_id}/uvl` persiste UVL y retorna `analysis_task_id`.                                                                                                                                                                                               |
| **Condiciones de ejecución** | - Versión existente del modelo<br>- Usuario propietario/superusuario<br>- Celery/Redis disponibles                                                                                                                                                                                                                |
| **Pasos de ejecución**       | 1. Enviar `PUT /api/v1/feature-models/{model_id}/versions/{version_id}/uvl` con UVL válido.<br>2. Validar HTTP 200.<br>3. Verificar `source="stored"` y `analysis_task_id` en respuesta.<br>4. Consultar `GET /api/v1/feature-models/{model_id}/versions/{version_id}/uvl`.<br>5. Confirmar contenido persistido. |
| **Resultado esperada**       | - UVL guardado en versión.<br>- Se encola tarea de análisis.<br>- Recuperación posterior coincide con contenido enviado.                                                                                                                                                                                          |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                                                                            |

### Caso de Prueba: INT_FM_CTRL_012

| Campo                        | Valor                                                                                                                                                                                                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_012                                                                                                                                                                                                                                                 |
| **HU**                       | HU10 - Integración y Sincronización UVL                                                                                                                                                                                                                         |
| **Nombre**                   | Aplicar UVL a estructura creando nueva versión                                                                                                                                                                                                                  |
| **Descripción**              | Verificar que `POST /feature-models/{model_id}/versions/{version_id}/uvl/apply-to-structure` crea versión estructurada desde UVL.                                                                                                                               |
| **Condiciones de ejecución** | - Versión base existente<br>- UVL de entrada válido                                                                                                                                                                                                             |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-models/{model_id}/versions/{version_id}/uvl/apply-to-structure`.<br>2. Validar HTTP 201.<br>3. Verificar nuevo `version_id` retornado.<br>4. Consultar estructura de la nueva versión (features/grupos/relaciones/constraints). |
| **Resultado esperada**       | - Nueva versión creada con estructura derivada del UVL.<br>- Versión fuente no se altera.<br>- Se retorna `analysis_task_id` para procesamiento posterior.                                                                                                      |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                          |

---

## HU11: Validación y Análisis del Modelo

### Caso de Prueba: INT_FM_CTRL_013

| Campo                        | Valor                                                                                                                                                                                                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_013                                                                                                                                                                                                                                                   |
| **HU**                       | HU11 - Validación Lógica y Estructural del Modelo                                                                                                                                                                                                                 |
| **Nombre**                   | Validación integral del modelo                                                                                                                                                                                                                                    |
| **Descripción**              | Verificar que `POST /feature-models/{model_id}/versions/{version_id}/validation/full` devuelve resultado compuesto (lógica + estructura + análisis).                                                                                                              |
| **Condiciones de ejecución** | - Versión existente con features y restricciones<br>- Usuario autenticado                                                                                                                                                                                         |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-models/{model_id}/versions/{version_id}/validation/full`.<br>2. Validar HTTP 200.<br>3. Confirmar presencia de secciones `logical`, `structure`, `analysis`.<br>4. Revisar coherencia de `is_valid` y listas de errores/warnings. |
| **Resultado esperada**       | - Contrato de respuesta completo y consistente.<br>- Sin errores de serialización.<br>- Métricas/issue list alineadas con datos del modelo.                                                                                                                       |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                            |

### Caso de Prueba: INT_FM_CTRL_014

| Campo                        | Valor                                                                                                                                                                                                                                                                                           |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_014                                                                                                                                                                                                                                                                                 |
| **HU**                       | HU11 - Validación Lógica y Estructural del Modelo                                                                                                                                                                                                                                               |
| **Nombre**                   | Resumen de análisis avanzado                                                                                                                                                                                                                                                                    |
| **Descripción**              | Verificar `POST /feature-models/{model_id}/versions/{version_id}/analysis/summary` y su payload analítico.                                                                                                                                                                                      |
| **Condiciones de ejecución** | - Versión existente y accesible<br>- Usuario autorizado                                                                                                                                                                                                                                         |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/feature-models/{model_id}/versions/{version_id}/analysis/summary` con `max_solutions` y `analysis_types` opcionales.<br>2. Validar HTTP 200.<br>3. Verificar campos: `satisfiable`, `dead_features`, `core_features`, `complexity_metrics`, `estimated_configurations`. |
| **Resultado esperada**       | - Resumen calculado correctamente.<br>- Campos obligatorios presentes y tipados.<br>- Resultado reproducible con mismo input/base de datos.                                                                                                                                                     |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                                                          |

---

## HU6: Métricas y Exportación

### Caso de Prueba: INT_FM_CTRL_015

| Campo                        | Valor                                                                                                                                                                                                                                                                                          |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_015                                                                                                                                                                                                                                                                                |
| **HU**                       | HU6 - Análisis de Métricas y Exportación                                                                                                                                                                                                                                                       |
| **Nombre**                   | Exportar última versión publicada en Mermaid                                                                                                                                                                                                                                                   |
| **Descripción**              | Verificar `GET /feature-models/{model_id}/versions/latest/export/mermaid` incluyendo persistencia de artefacto de exportación.                                                                                                                                                                 |
| **Condiciones de ejecución** | - Existe al menos una versión `PUBLISHED`<br>- MinIO y Redis operativos                                                                                                                                                                                                                        |
| **Pasos de ejecución**       | 1. Ejecutar `GET /api/v1/feature-models/{model_id}/versions/latest/export/mermaid`.<br>2. Validar HTTP 200 y `Content-Type` de texto.<br>3. Verificar cabecera `Content-Disposition`.<br>4. Consultar `GET /api/v1/feature-models/{model_id}/exports` para confirmar cache/indexado de export. |
| **Resultado esperada**       | - Contenido Mermaid válido.<br>- Export registrado en cache y almacenamiento de objetos.<br>- URL de descarga disponible en listado de exports.                                                                                                                                                |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                                                         |

### Caso de Prueba: INT_FM_CTRL_016

| Campo                        | Valor                                                                                                                                                                                                                                                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_016                                                                                                                                                                                                                                                                                               |
| **HU**                       | HU6 - Análisis de Métricas y Exportación                                                                                                                                                                                                                                                                      |
| **Nombre**                   | Obtener estadísticas de última versión publicada                                                                                                                                                                                                                                                              |
| **Descripción**              | Verificar `GET /feature-models/{model_id}/versions/latest/statistics` y exactitud mínima de métricas.                                                                                                                                                                                                         |
| **Condiciones de ejecución** | - FM existente con versión `PUBLISHED`                                                                                                                                                                                                                                                                        |
| **Pasos de ejecución**       | 1. Ejecutar `GET /api/v1/feature-models/{model_id}/versions/latest/statistics`.<br>2. Validar HTTP 200.<br>3. Verificar campos esperados (`total_features`, `total_groups`, `total_relations`, `total_constraints`, `max_tree_depth`, etc.).<br>4. Contrastar al menos 2 métricas con consulta directa de BD. |
| **Resultado esperada**       | - Métricas consistentes con la estructura almacenada.<br>- Contrato de respuesta completo.<br>- Sin desalineación entre repositorio y cálculo estadístico.                                                                                                                                                    |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                                                                        |

---

## HU12/HU13: Configuraciones

### Caso de Prueba: INT_FM_CTRL_017

| Campo                        | Valor                                                                                                                                                                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_017                                                                                                                                                                                                                                       |
| **HU**                       | HU12 - Gestión de Configuraciones                                                                                                                                                                                                                     |
| **Nombre**                   | Crear configuración válida                                                                                                                                                                                                                            |
| **Descripción**              | Verificar que `POST /configurations/` valida selección de features y persiste configuración solo si es válida.                                                                                                                                        |
| **Condiciones de ejecución** | - Versión de FM existente<br>- Conjunto de features que cumple restricciones                                                                                                                                                                          |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/configurations/` con `feature_model_version_id` y `feature_ids` válidos.<br>2. Validar HTTP 200/201 según contrato actual.<br>3. Recuperar configuración por ID.<br>4. Verificar relación con versión y features persistidos. |
| **Resultado esperada**       | - Configuración creada y almacenada.<br>- Validación lógica aplicada antes de persistir.<br>- Estructura de respuesta correcta.                                                                                                                       |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                |

### Caso de Prueba: INT_FM_CTRL_018

| Campo                        | Valor                                                                                                                                                                                                                                                                         |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID de prueba**             | INT_FM_CTRL_018                                                                                                                                                                                                                                                               |
| **HU**                       | HU13 - Validación y Generación Automática de Configuraciones                                                                                                                                                                                                                  |
| **Nombre**                   | Generación automática de configuraciones                                                                                                                                                                                                                                      |
| **Descripción**              | Verificar `POST /configurations/generate` para múltiples resultados y métrica de calidad.                                                                                                                                                                                     |
| **Condiciones de ejecución** | - Versión satisfacible<br>- Motor de generación habilitado                                                                                                                                                                                                                    |
| **Pasos de ejecución**       | 1. Enviar `POST /api/v1/configurations/generate` con `feature_model_version_id`, `count`, `strategy`.<br>2. Validar HTTP 200.<br>3. Verificar que `results` tenga tamaño `<= count` y elementos con `success`/`selected_features`.<br>4. Verificar objeto `quality` no vacío. |
| **Resultado esperada**       | - Se devuelven configuraciones válidas.<br>- El límite solicitado se respeta.<br>- Métricas de calidad disponibles para evaluación.                                                                                                                                           |
| **Evaluación de la prueba**  | **Pendiente** (PASS/FAIL + evidencia).                                                                                                                                                                                                                                        |

---

## Criterio de evaluación sugerido (para cada caso)

- **PASS**: endpoint cumple contrato HTTP + estructura de respuesta + efectos esperados en persistencia/cola/cache.
- **FAIL**: incumple contrato, genera efectos colaterales no esperados o no conserva integridad de datos.
- **Bloqueada**: no ejecutable por dependencia externa (credenciales, cola, MinIO, datos semilla).
