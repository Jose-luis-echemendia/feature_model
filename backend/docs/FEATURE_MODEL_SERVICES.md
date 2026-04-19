# Servicios de Feature Model (FM)

Este documento describe, de forma detallada, los servicios implementados en el módulo de Feature Model. Cada servicio cumple un rol específico dentro del ciclo de vida de los modelos: validación lógica, generación de configuraciones, análisis estructural, construcción de árboles, exportación de formatos, versionado y gestión de UVL.

## 1) FeatureModelLogicalValidator (Validador lógico SAT/SMT)

**Objetivo**

- Verificar la consistencia lógica global de un Feature Model.
- Asegurar satisfacibilidad de restricciones y relaciones.

**Qué hace**

- Construye variables booleanas para cada feature.
- Codifica jerarquías (mandatory/optional), grupos (OR/XOR) y restricciones cross-tree (requires/excludes, etc.).
- Verifica satisfacibilidad completa del modelo y de configuraciones específicas.
- Soporta validación de selecciones parciales con cache.
- Permite enumerar configuraciones válidas (cuando se utiliza en conjunto con el generador).

**Niveles/técnicas**

- **Nivel 1 (SymPy)**: validación simbólica para modelos pequeños.
- **Nivel 2 (PySAT)**: SAT solving escalable para modelos medianos/grandes.
- **Nivel 3 (Z3)**: SMT/optimización para análisis avanzados.

**Funcionalidades principales**

- `validate_feature_model(...)`: valida el modelo completo (satisfacibilidad global).
- `validate_configuration(...)`: valida una selección concreta de features.
- `is_partial_selection_satisfiable(...)`: valida decisiones parciales.
- Conversión y compatibilidad con distintos backends (SymPy/PySAT/Z3).

**Resultado/artefactos**

- `FeatureModelValidationResult` con `is_valid`, `errors`, `warnings` y asignación satisfactoria (si existe).

---

## 2) FeatureModelConfigurationGenerator (Generador de configuraciones)

**Objetivo**

- Generar configuraciones válidas completas o completar decisiones parciales.
- Proponer soluciones diversas o bien optimizadas según estrategia.

**Qué hace**

- Usa validación lógica para asegurar que las configuraciones cumplan todas las restricciones.
- Puede generar una configuración única o múltiples configuraciones diversas.

**Estrategias soportadas**

- **GREEDY**: determinista, rápida, prioriza mandatory.
- **RANDOM**: estocástica, fomenta diversidad.
- **BEAM_SEARCH**: balance entre exploración y eficiencia.
- **GENETIC (DEAP)**: búsqueda evolutiva multi-objetivo.
- **SAT_ENUM**: enumeración por SAT (cuando está disponible).
- **PAIRWISE / UNIFORM / STRATIFIED**: muestreo para cobertura.
- **CP_SAT (OR-Tools)**: programación con restricciones.
- **BDD**: muestreo usando diagramas de decisión binaria.
- **NSGA2**: optimización multi-objetivo.

**Funcionalidades principales**

- `generate_valid_configuration(...)`: genera una configuración válida con estrategia.
- `complete_partial_configuration(...)`: completa selecciones parciales.
- `generate_multiple_configurations(...)`: genera conjuntos de configuraciones diversas.

**Resultado/artefactos**

- `GenerationResult` con `success`, configuración, features seleccionadas, score, iteraciones y errores.

---

## 3) FeatureModelStructuralAnalyzer (Analizador estructural)

**Objetivo**

- Analizar propiedades topológicas del modelo (más allá de la lógica pura).
- Detectar problemas estructurales y métricas de complejidad.

**Qué hace**

- Construye grafos de dependencias y jerarquía.
- Analiza alcanzabilidad, redundancias y relaciones implícitas.
- Calcula métricas de impacto y complejidad.

**Análisis disponibles**

- **Dead features**: features inaccesibles desde la raíz.
- **Redundancias**: relaciones o constraints duplicadas.
- **Relaciones implícitas**: dependencias no explícitas en la jerarquía.
- **Dependencias transitivas**: efectos indirectos entre features.
- **Componentes fuertemente conexas (SCC)**: ciclos y conectividad.
- **Métricas**: centralidad, complejidad, profundidad, impacto.

**Funcionalidades principales**

- `analyze_feature_model(...)`: análisis completo por tipo.
- `detect_dead_features(...)`: lista de features muertas.
- `calculate_feature_impact(...)`: métricas de impacto por feature.

**Resultado/artefactos**

- `StructuralAnalysisResult` con `issues`, `metrics` y datos de grafo.

---

## 4) FeatureModelTreeBuilder (Constructor de árbol)

**Objetivo**

- Construir la representación completa del Feature Model para consumo en frontend/API.

**Qué hace**

- Construye el árbol jerárquico anidado con metadata.
- Genera lista de relaciones y constraints con descripciones legibles.
- Calcula estadísticas agregadas (totales, profundidad, grupos, etc.).
- Incluye recursos y tags asociados a features (si aplica).

**Funcionalidades principales**

- `build_complete_response(...)`: respuesta completa con árbol, relaciones, constraints y estadísticas.

**Resultado/artefactos**

- `FeatureModelCompleteResponse` con:
  - información del modelo
  - información de versión
  - árbol jerárquico
  - relaciones y constraints
  - estadísticas y metadata
  - UVL efectivo (persistido o generado)

---

## 5) FeatureModelExportService (Exportador de formatos)

**Objetivo**

- Exportar el Feature Model a formatos estándar para herramientas externas.

**Qué hace**

- Mapea UUIDs a identificadores numéricos para formatos SAT/externos.
- Genera representaciones en múltiples estándares.

**Formatos soportados**

- FeatureIDE XML
- SPLOT XML (placeholder)
- TVL (placeholder)
- DIMACS CNF
- JSON
- UVL
- DOT (Graphviz)
- Mermaid

**Funcionalidades principales**

- `export(format)`: exporta según formato.
- `export_to_featureide_xml()`, `export_to_dimacs()`, `export_to_json()`, `export_to_uvl()`, etc.

**Resultado/artefactos**

- Cadena de texto con el contenido exportado en el formato seleccionado.

---

## 6) FeatureModelVersionManager (Gestor de versionado)

**Objetivo**

- Gestionar el ciclo de vida de versiones del Feature Model.
- Garantizar trazabilidad, inmutabilidad y reproducibilidad.

**Qué hace**

- Crea nuevas versiones (vacías o clonadas).
- Publica, archiva y restaura versiones.
- Genera snapshots completos con mapeos UUID↔Integer y estadísticas.
- Controla estados (DRAFT, PUBLISHED, ARCHIVED).

**Funcionalidades principales**

- `create_new_version(...)`: crea versiones nuevas.
- `publish_version(...)`: publica y genera snapshot.
- `archive_version(...)` y `restore_version(...)`: gestión de estados.
- Construcción interna de snapshots y estadísticas.

**Resultado/artefactos**

- `FeatureModelVersion` persistida.
- Snapshot completo (estructura, estadísticas, mapping, metadata).

---

## 7) FeatureModelUVLImporter (Importador UVL)

**Objetivo**

- Importar especificaciones UVL y materializarlas como estructura FM.
- Validar UVL en fases: parseo, estructura, constraints simples y diff.

**Qué hace**

- Parsea UVL en una estructura intermedia (nodos, grupos, constraints).
- Valida estructura: raíz única, ciclos, cardinalidad mínima de grupos.
- Convierte UVL a entidades del modelo (features, grupos, relaciones, constraints).
- Permite comparar un UVL contra una versión existente (diff).

**Funcionalidades principales**

- `validate_uvl_only(...)`: valida sin persistir.
- `apply_uvl(...)`: crea versión y estructura a partir de UVL.
- `diff_uvl(...)`: compara UVL con la versión actual.

**Resultado/artefactos**

- Nueva versión del Feature Model con estructura creada.
- Reportes de validación o diferencias.

---

## 8) Facade de análisis (fm_analysis_facade)

**Objetivo**

- Orquestar análisis de alto nivel combinando validación lógica, análisis estructural y métricas derivadas.

**Qué hace**

- Construye payloads desde la versión.
- Ejecuta validación lógica y análisis estructural.
- Calcula métricas derivadas: core/commonality, atomic sets y estimación de configuraciones.
- Integra validación UVL opcional y validación adicional con Flamapy cuando está disponible.

**Funcionalidades principales**

- `analyze_version(...)`: resumen completo de análisis.
- `compare_versions(...)`: compara métricas entre dos versiones.

**Resultado/artefactos**

- `AnalysisSummary` con satisfacibilidad, errores, warnings, core features, métricas y validaciones UVL.

---

## Resumen general del objetivo del módulo

El módulo de servicios de Feature Model busca **garantizar la calidad, consistencia, trazabilidad y utilidad operativa** de los modelos de características. En conjunto:

- **Valida** la lógica y restricciones del modelo.
- **Genera** configuraciones válidas para derivación de productos.
- **Analiza** la estructura para detectar problemas y métricas clave.
- **Construye** la representación completa para consumo de APIs/Frontend.
- **Exporta** a estándares interoperables.
- **Versiona** para asegurar evolución y reproducibilidad.
- **Importa** UVL para integrar modelos externos.
