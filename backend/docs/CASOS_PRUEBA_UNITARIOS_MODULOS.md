# Casos de Pruebas Unitarias por Módulo

Este documento define casos de prueba unitarios para los módulos de:

- `services`
- `repositories`
- `exceptions`

Formato por caso:

- **Descripción**
- **Entrada**
- **Salida esperada**
- **Evaluación de la prueba**

---

## 1) Servicios

### Caso: SVC_FM_VERSION_001 — Crear nueva versión vacía

- **Descripción:** Verificar que `FeatureModelVersionManager.create_new_version(source_version=None)` crea una versión en estado `DRAFT` con `version_number` consecutivo.
- **Entrada:**
  - `feature_model.id` válido.
  - Mock de `repository.get_latest_version_number()` retornando `3`.
  - `source_version=None`.
- **Salida esperada:**
  - Nueva versión con `version_number=4`.
  - `status=DRAFT`.
  - Se ejecuta `session.commit()` y `session.refresh()`.
- **Evaluación de la prueba:**
  - **Pasa** si se cumplen valores y llamadas a sesión.
  - **Falla** si no incrementa versión o no persiste cambios.

### Caso: SVC_FM_VERSION_002 — Publicar versión en estado inválido

- **Descripción:** Verificar que `publish_version()` rechaza publicar si la versión no está en `DRAFT`.
- **Entrada:**
  - Versión con `status=PUBLISHED`.
  - `validate=True`.
- **Salida esperada:**
  - Se lanza `InvalidVersionStateException`.
  - No se hace `commit`.
- **Evaluación de la prueba:**
  - **Pasa** si lanza excepción exacta y no persiste.
  - **Falla** si permite transición inválida.

### Caso: SVC_FM_VERSION_003 — Archivar versión publicada

- **Descripción:** Verificar que `archive_version()` cambia `PUBLISHED -> ARCHIVED`.
- **Entrada:**
  - Versión con `status=PUBLISHED`.
- **Salida esperada:**
  - `status=ARCHIVED`.
  - Se ejecuta `commit` y `refresh`.
- **Evaluación de la prueba:**
  - **Pasa** si transición y persistencia son correctas.
  - **Falla** si estado final no es `ARCHIVED`.

### Caso: SVC_FM_EXPORT_001 — Formato no soportado

- **Descripción:** Verificar que `FeatureModelExportService.export()` falla con formato inválido.
- **Entrada:**
  - Valor de formato no incluido en `ExportFormat` soportados.
- **Salida esperada:**
  - `ValueError` con mensaje de formato no soportado.
- **Evaluación de la prueba:**
  - **Pasa** si se eleva `ValueError` y no retorna contenido.
  - **Falla** si intenta exportar sin validar formato.

### Caso: SVC_FM_EXPORT_002 — Exportación JSON válida

- **Descripción:** Verificar que `export(ExportFormat.JSON)` retorna contenido serializable.
- **Entrada:**
  - Versión con features/constraints mínimas.
- **Salida esperada:**
  - Cadena JSON válida.
  - Incluye metadatos de modelo y versión.
- **Evaluación de la prueba:**
  - **Pasa** si `json.loads()` no falla y contiene campos esperados.
  - **Falla** si retorna contenido inválido o incompleto.

### Caso: SVC_FM_UVL_001 — Validación UVL correcta sin persistencia

- **Descripción:** Verificar que `FeatureModelUVLImporter.validate_uvl_only()` valida estructura UVL y no persiste datos.
- **Entrada:**
  - UVL válido con sección `features` y opcional `constraints`.
- **Salida esperada:**
  - Resultado con `is_valid=True`, `root`, conteo de `features` y `constraints`.
  - Sin llamadas a `session.commit()`.
- **Evaluación de la prueba:**
  - **Pasa** si valida y no modifica BD.
  - **Falla** si persiste o retorna estructura incorrecta.

### Caso: SVC_FM_UVL_002 — Error por indentación inválida

- **Descripción:** Verificar que `_parse_uvl()` dispara error cuando la indentación no es múltiplo de 4.
- **Entrada:**
  - UVL con línea indentada con 2 espacios.
- **Salida esperada:**
  - `UVLParseError` con detalle de indentación inválida.
- **Evaluación de la prueba:**
  - **Pasa** si se captura `UVLParseError`.
  - **Falla** si el parser acepta contenido mal indentado.

### Caso: SVC_FM_UVL_003 — Aplicar UVL y persistir contenido

- **Descripción:** Verificar que `apply_uvl()` crea una nueva versión, estructura de features y guarda `uvl_content`.
- **Entrada:**
  - UVL válido.
  - Mocks de sesión y `FeatureModelVersionManager.create_new_version()`.
- **Salida esperada:**
  - Nueva versión con `uvl_content` persistido.
  - Features creadas con jerarquía válida.
  - `commit` y `refresh` ejecutados.
- **Evaluación de la prueba:**
  - **Pasa** si crea estructura y persiste contenido.
  - **Falla** si no crea versión o no guarda UVL.

### Caso: SVC_FM_ANALYSIS_001 — Análisis exitoso con validación UVL

- **Descripción:** Verificar que `analyze_version()` combina resultados lógicos/estructurales y añade `uvl_validation` cuando hay contenido UVL.
- **Entrada:**
  - Versión con features y `uvl_content`.
  - Mocks de `FeatureModelLogicalValidator`, `FeatureModelStructuralAnalyzer` y `validate_uvl_only`.
- **Salida esperada:**
  - `AnalysisSummary` con `satisfiable`, `dead_features`, `commonality`, `complexity_metrics`.
  - `uvl_validation` presente.
- **Evaluación de la prueba:**
  - **Pasa** si el summary contiene datos agregados esperados.
  - **Falla** si omite integración de validadores.

### Caso: SVC_FM_ANALYSIS_002 — Comparación entre versiones

- **Descripción:** Verificar que `compare_versions()` calcula deltas de `dead_features`, `core_features` y configuraciones.
- **Entrada:**
  - `base_version` y `target_version` con diferencias controladas (mocks).
- **Salida esperada:**
  - Diccionario con claves `base`, `target`, `delta`.
  - Listas de `*_added` y `*_removed` coherentes.
- **Evaluación de la prueba:**
  - **Pasa** si los deltas coinciden con el escenario.
  - **Falla** si compara mal o mezcla resultados.

---

## 2) Repositorios

### Caso: REP_BASE_USER_001 — Email único (duplicado)

- **Descripción:** Verificar que `BaseUserRepository.validate_email_unique()` lanza error si existe usuario.
- **Entrada:**
  - `existing_user` no nulo.
- **Salida esperada:**
  - `ValueError` con mensaje de email ya registrado.
- **Evaluación de la prueba:**
  - **Pasa** si bloquea duplicado.
  - **Falla** si permite continuar.

### Caso: REP_BASE_DOMAIN_001 — Nombre de dominio único en actualización propia

- **Descripción:** Verificar que `BaseDomainRepository.validate_name_unique()` permite mismo nombre cuando `existing_domain.id == current_domain_id`.
- **Entrada:**
  - `existing_domain.id` igual a `current_domain_id`.
- **Salida esperada:**
  - No excepción.
- **Evaluación de la prueba:**
  - **Pasa** si no falla en auto-actualización.
  - **Falla** si bloquea un caso válido.

### Caso: REP_BASE_FEATURE_001 — Validar padre distinto de sí mismo

- **Descripción:** Verificar que `validate_parent_not_self(feature_id, parent_id)` rechaza autorreferencia.
- **Entrada:**
  - `feature_id == parent_id`.
- **Salida esperada:**
  - `ValueError` indicando que no puede ser su propio padre.
- **Evaluación de la prueba:**
  - **Pasa** si detecta autorreferencia.
  - **Falla** si permite ciclo trivial.

### Caso: REP_BASE_FEATURE_002 — Construcción de árbol de features

- **Descripción:** Verificar que `build_feature_tree()` transforma lista plana en árbol por `parent_id`.
- **Entrada:**
  - Lista de features con una raíz y dos hijos.
- **Salida esperada:**
  - Lista con 1 raíz y 2 nodos en `children`.
- **Evaluación de la prueba:**
  - **Pasa** si jerarquía coincide.
  - **Falla** si pierde nodos o relaciones.

### Caso: REP_BASE_RELATION_001 — Features en misma versión

- **Descripción:** Verificar que `validate_same_version()` falla cuando origen/destino pertenecen a distintas versiones.
- **Entrada:**
  - `source_feature.feature_model_version_id != target_feature.feature_model_version_id`.
- **Salida esperada:**
  - `ValueError` indicando incompatibilidad de versión.
- **Evaluación de la prueba:**
  - **Pasa** si bloquea relaciones entre versiones distintas.
  - **Falla** si permite inconsistencia.

### Caso: REP_DOMAIN_001 — Crear dominio exitoso

- **Descripción:** Verificar `DomainRepository.create()` con datos válidos.
- **Entrada:**
  - `DomainCreate(name, description)` válido.
- **Salida esperada:**
  - Entidad `Domain` creada y persistida.
  - `is_active=True` por defecto (si aplica en modelo).
- **Evaluación de la prueba:**
  - **Pasa** si persiste y retorna entidad consistente.
  - **Falla** si omite persistencia o retorna datos incompletos.

### Caso: REP_USER_001 — Autenticación correcta

- **Descripción:** Verificar que `UserRepository.authenticate(email, password)` retorna usuario al recibir credenciales válidas.
- **Entrada:**
  - Usuario existente.
  - Mock de verificación de hash retornando `True`.
- **Salida esperada:**
  - Retorna instancia de `User`.
- **Evaluación de la prueba:**
  - **Pasa** si autentica correctamente.
  - **Falla** si retorna `None` con credenciales válidas.

### Caso: REP_USER_002 — Autenticación fallida

- **Descripción:** Verificar que `authenticate()` retorna `None` con password inválida.
- **Entrada:**
  - Usuario existente.
  - Verificador de hash retornando `False`.
- **Salida esperada:**
  - `None`.
- **Evaluación de la prueba:**
  - **Pasa** si no autentica credenciales inválidas.
  - **Falla** si devuelve usuario.

### Caso: REP_FM_VERSION_001 — Siguiente número de versión

- **Descripción:** Verificar que `FeatureModelVersionRepository.get_latest_version_number()` retorna `0` cuando no hay versiones y el máximo correcto cuando sí existen.
- **Entrada:**
  - Escenario A: sin registros.
  - Escenario B: versiones con `version_number` [1,2,4].
- **Salida esperada:**
  - A: `0`.
  - B: `4`.
- **Evaluación de la prueba:**
  - **Pasa** si calcula correctamente en ambos escenarios.
  - **Falla** si retorna `None` o valor incorrecto.

### Caso: REP_FM_VERSION_002 — Estadísticas de versión

- **Descripción:** Verificar `get_statistics(version_id)` con features, grupos, constraints y relaciones.
- **Entrada:**
  - Versión con datos de prueba predecibles.
- **Salida esperada:**
  - Diccionario con contadores correctos (`features`, `groups`, `constraints`, `relations`, etc.).
- **Evaluación de la prueba:**
  - **Pasa** si contadores coinciden con fixtures.
  - **Falla** si hay desalineación en métricas.

---

## 3) Excepciones

### Caso: EXC_HANDLER_001 — `_extract_object_from_request()`

- **Descripción:** Verificar normalización de objeto a partir de path y método HTTP.
- **Entrada:**
  - Request con path `/api/v1/models/123/versions` y método `GET`.
- **Salida esperada:**
  - Objeto `model.get`.
- **Evaluación de la prueba:**
  - **Pasa** si remueve prefijos (`api`, `v1`) y singulariza recurso.
  - **Falla** si retorna objeto no normalizado.

### Caso: EXC_HANDLER_002 — `validation_exception_handler()`

- **Descripción:** Verificar que un `RequestValidationError` genera respuesta estandarizada HTTP 422.
- **Entrada:**
  - Request válido + excepción de validación con errores de campos.
- **Salida esperada:**
  - `JSONResponse` con `status_code=422`.
  - `message.category=request_validation`.
  - `message.error_code=1001`.
- **Evaluación de la prueba:**
  - **Pasa** si estructura y código de error son correctos.
  - **Falla** si cambia contrato de error.

### Caso: EXC_HANDLER_003 — `http_exception_handler()`

- **Descripción:** Verificar mapeo de códigos para `HTTPException` (ej. 404).
- **Entrada:**
  - `HTTPException(status_code=404, detail="Not Found")`.
- **Salida esperada:**
  - `JSONResponse` con `code=404`, `error_code=1005`, `category=http_error`.
- **Evaluación de la prueba:**
  - **Pasa** si usa mapa `_ERROR_CODE_MAP`.
  - **Falla** si devuelve código/mensaje inconsistente.

### Caso: EXC_HANDLER_004 — `generic_exception_handler()`

- **Descripción:** Verificar respuesta controlada para errores no esperados.
- **Entrada:**
  - `Exception("boom")`.
- **Salida esperada:**
  - HTTP 500.
  - Mensaje genérico sin filtrar detalle interno.
  - `error_code=5000`.
- **Evaluación de la prueba:**
  - **Pasa** si no expone detalles sensibles y respeta contrato.
  - **Falla** si filtra stack/error interno al cliente.

### Caso: EXC_BASE_001 — `NotFoundException`

- **Descripción:** Verificar que `NotFoundException` inicializa con código 404.
- **Entrada:**
  - `NotFoundException("X no encontrado")`.
- **Salida esperada:**
  - `status_code=404`, `detail="X no encontrado"`.
- **Evaluación de la prueba:**
  - **Pasa** si hereda y configura correctamente.
  - **Falla** si código HTTP no coincide.

### Caso: EXC_BASE_002 — `BusinessLogicException`

- **Descripción:** Verificar inicialización de excepción de negocio.
- **Entrada:**
  - `BusinessLogicException("Regla inválida")`.
- **Salida esperada:**
  - `status_code=400`, `detail` correcto.
- **Evaluación de la prueba:**
  - **Pasa** si estado y detalle son correctos.
  - **Falla** si usa código distinto.

### Caso: EXC_DOMAIN_001 — `DomainAlreadyExistsException`

- **Descripción:** Verificar mensaje contextual cuando dominio existe.
- **Entrada:**
  - `domain_name="Ingeniería de Software"`.
- **Salida esperada:**
  - Excepción tipo `ConflictException` (409).
  - Mensaje incluyendo nombre del dominio conflictivo.
- **Evaluación de la prueba:**
  - **Pasa** si conserva semántica y contexto.
  - **Falla** si mensaje pierde identificador clave.

### Caso: EXC_FM_001 — `InvalidVersionStateException`

- **Descripción:** Verificar composición de mensaje para transición inválida de versión.
- **Entrada:**
  - `current_state="published"`, `required_state="draft"`, `operation="publish version"`.
- **Salida esperada:**
  - Excepción de negocio con mensaje que incluya estado actual, requerido y operación.
- **Evaluación de la prueba:**
  - **Pasa** si mensaje es trazable para depuración.
  - **Falla** si omite contexto de transición.

### Caso: EXC_FM_002 — `MissingRootFeatureException`

- **Descripción:** Verificar que se lanza excepción procesable cuando no existe raíz en el árbol.
- **Entrada:**
  - Instancia directa de `MissingRootFeatureException()`.
- **Salida esperada:**
  - Tipo `UnprocessableEntityException` con HTTP 422.
- **Evaluación de la prueba:**
  - **Pasa** si mantiene clasificación semántica (error estructural 422).
  - **Falla** si cambia a otro código.

---

## Recomendaciones de implementación

1. Usar `pytest` + `pytest-asyncio` para casos asíncronos.
2. Mockear sesión (`AsyncSession`) y repositorios en pruebas de servicios para aislar lógica.
3. Para repositorios, combinar:
   - Unit tests puros (helpers base)
   - Tests con BD de pruebas para consultas SQLModel.
4. Validar contrato de errores (`code`, `status`, `message`) para asegurar estabilidad de API.
