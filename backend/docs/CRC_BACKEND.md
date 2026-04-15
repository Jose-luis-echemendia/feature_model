# Tablas CRC del backend

Ámbito: clases principales del backend (modelos de dominio y servicios de aplicación).

---

## Identidad y acceso

| Clase  | Responsabilidades                                                                                                        | Colaboradores                                                                            |
| ------ | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `User` | • Representar usuarios y roles • Mantener estado activo/inactivo • Soportar auditoría (creado/actualizado/eliminado por) | `FeatureModel` (owner/collaborator), `FeatureModelCollaborator`, repositorios de usuario |

---

## Gobernanza de dominios y modelos

| Clase                 | Responsabilidades                                                                                                                    | Colaboradores                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `Domain`              | • Agrupar modelos por dominio • Mantener metadatos (nombre, descripción) • Gestionar relación con modelos                            | `FeatureModel`                                                                              |
| `FeatureModel`        | • Representar un FM (nombre, descripción, dominio) • Enlazar propietario y versiones • Mantener colaboradores                        | `Domain`, `User`, `FeatureModelVersion`, `FeatureModelCollaborator`                         |
| `FeatureModelVersion` | • Versionar un FM (estado, snapshot, UVL) • Enlazar estructura completa (features, grupos, relaciones, constraints, configuraciones) | `FeatureModel`, `Feature`, `FeatureGroup`, `FeatureRelation`, `Constraint`, `Configuration` |

---

## Estructura de variabilidad

| Clase             | Responsabilidades                                                                                                                                     | Colaboradores                                                                                |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `Feature`         | • Representar característica (nombre, tipo, propiedades) • Mantener jerarquía padre/hijos • Enlazar grupo y recurso • Soportar tags y configuraciones | `FeatureModelVersion`, `FeatureGroup`, `FeatureRelation`, `Tag`, `Configuration`, `Resource` |
| `FeatureGroup`    | • Definir agrupaciones XOR/OR • Controlar cardinalidades • Enlazar feature padre y miembros                                                           | `FeatureModelVersion`, `Feature`                                                             |
| `FeatureRelation` | • Representar relaciones cross-tree (requires/excludes)                                                                                               | `FeatureModelVersion`, `Feature`                                                             |
| `Constraint`      | • Persistir restricciones lógicas complejas (expr_text, expr_cnf)                                                                                     | `FeatureModelVersion`                                                                        |

---

## Configuración y derivación

| Clase           | Responsabilidades                                                                  | Colaboradores                           |
| --------------- | ---------------------------------------------------------------------------------- | --------------------------------------- |
| `Configuration` | • Persistir selección de features • Enlazar tags • Mantener estado activo/inactivo | `FeatureModelVersion`, `Feature`, `Tag` |

---

## Taxonomías y recursos

| Clase      | Responsabilidades                                                                                  | Colaboradores              |
| ---------- | -------------------------------------------------------------------------------------------------- | -------------------------- |
| `Tag`      | • Clasificar features/configuraciones • Mantener unicidad por nombre                               | `Feature`, `Configuration` |
| `Resource` | • Representar recursos educativos • Mantener metadatos de contenido/licencia • Enlazar propietario | `User`, `Feature`          |

---

## Servicios de aplicación

| Clase                                | Responsabilidades                                                                                                     | Colaboradores                                                                                                           |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `FeatureModelVersionManager`         | • Crear versiones (copy-on-write) • Publicar/archivar/restaurar • Generar snapshot y validaciones de transición       | `FeatureModelVersionRepository`, `FeatureModelVersion`, `Feature`, `User`, `FeatureModel`                               |
| `FeatureModelExportService`          | • Exportar FM a UVL/XML/TVL/DIMACS/JSON/DOT/Mermaid • Construir mapeo UUID↔int                                        | `FeatureModelVersion`, `Feature`, `Constraint`, enums de exportación                                                    |
| `FeatureModelUVLImporter`            | • Validar UVL • Construir estructura desde UVL • Crear relaciones/constraints y nueva versión                         | `FeatureModelVersionManager`, `Feature`, `FeatureGroup`, `FeatureRelation`, `Constraint`, `FeatureModelVersion`, `User` |
| `FeatureModelLogicalValidator`       | • Validación SAT/SMT (sympy/pysat/z3) • Verificar consistencia global y configuraciones                               | `InvalidConstraintException` y otras excepciones, dependencias SAT/SMT                                                  |
| `FeatureModelConfigurationGenerator` | • Generar configuraciones válidas • Estrategias GREEDY/RANDOM/BEAM/GENETIC/NSGA2 etc.                                 | `FeatureModelLogicalValidator`, `GenerationStrategy`, dependencias DEAP/OR-Tools/BDD                                    |
| `FeatureModelStructuralAnalyzer`     | • Analizar estructura (dead features, redundancias, SCC) • Métricas de complejidad                                    | `AnalysisType`, `networkx`, excepciones estructurales                                                                   |
| `FeatureModelTreeBuilder`            | • Construir árbol completo para respuesta • Generar estadísticas • UVL efectivo                                       | `FeatureModelVersion`, `Feature`, `FeatureGroup`, `FeatureModelExportService`, schemas `FeatureModelCompleteResponse`   |
| `FeatureModelAnalysisFacade`         | • Orquestar análisis lógico + estructural • Calcular commonality/core/atomic sets • Validación UVL (opcional Flamapy) | `FeatureModelLogicalValidator`, `FeatureModelStructuralAnalyzer`, `FeatureModelUVLImporter`                             |
| `SettingsService`                    | • Consultar/actualizar settings • Cachear en Redis                                                                    | `AppSetting`, `redis_client`                                                                                            |

---

## Configuración del sistema

| Clase        | Responsabilidades                                                  | Colaboradores                  |
| ------------ | ------------------------------------------------------------------ | ------------------------------ |
| `AppSetting` | • Persistir claves de configuración • Mantener descripción y valor | `SettingsService`, Redis cache |

---

Si quieres, genero CRC extendidas por repositorios y handlers (routers) o vinculo cada CRC con los RF e historias de usuario que compartiste.
