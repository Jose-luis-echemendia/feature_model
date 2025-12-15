# Estructura de Respuesta: Feature Model Completo (`/{version/latest}/complete/`)

Este endpoint devuelve una representación detallada y jerárquica de la última versión del feature model. La respuesta está optimizada para aplicaciones _single-page_ (SPA), proporcionando todos los datos necesarios para renderizar visualizaciones, configurar instancias y validar reglas sin necesidad de consultas adicionales.

## 📋 Estructura General

La respuesta JSON se divide en 7 secciones principales:

### 1. `feature_model` - Información del Modelo Base

- **Propósito:** Contiene los metadatos del feature model general (título, descripción, autor), independientemente de la versión.

- **Campos:**

  - `id` (UUID): Identificador único del feature model
  - `name` (string): Nombre descriptivo del modelo
  - `description` (string): Descripción detallada del propósito del modelo
  - `domain_id` (UUID): Referencia al dominio al que pertenece (ej: "Ingeniería Informática")
  - `domain_name` (string): Nombre legible del dominio
  - `owner_id` (UUID): Usuario creador del modelo
  - `created_at` (datetime): Fecha de creación
  - `updated_at` (datetime | null): Última actualización
  - `is_active` (boolean): Estado de activación del modelo

- **Ejemplo:**
  ```json
  {
    "id": "3fd31d5b-de5c-4ee1-9716-a564a611ce3a",
    "name": "Gestión de Proyectos Informáticos (GPI)",
    "description": "Asignatura completa sobre metodologías...",
    "domain_id": "e370f83f-e864-4d0d-8139-620a537227c4",
    "domain_name": "Ingeniería Informática",
    "owner_id": "75023ee0-4a41-4c9c-a927-e8d8c897d2ea",
    "created_at": "2025-12-05T07:49:13.476035",
    "updated_at": null,
    "is_active": true
  }
  ```

### 2. `version` - Información de la Versión Específica

- **Propósito:** Identifica la versión exacta que se está visualizando y proporciona mapeo UUID↔Integer para exportación.

- **Campos:**

  - `id` (UUID): Identificador único de la versión
  - `version_number` (int): Número secuencial de versión (1, 2, 3...)
  - `status` (enum): Estado del ciclo de vida: `"draft"`, `"in_review"`, `"published"`, `"archived"`
  - `snapshot` (object): Mapeo bidireccional para exportación
    - `int_to_uuid` (dict): Mapeo de IDs cortos (1,2,3...) → UUIDs
    - `uuid_to_int` (dict): Mapeo inverso UUIDs → IDs cortos
  - `created_at` (datetime): Fecha de creación de esta versión

- **¿Por qué el snapshot?**

  - **Exportación:** Herramientas externas (FeatureIDE, DIMACS) usan IDs numéricos cortos
  - **SAT Solvers:** Requieren variables numéricas secuenciales
  - **Debugging:** IDs cortos son más fáciles de leer que UUIDs
  - **Compatibilidad:** Interoperabilidad con formato SPLOT, DIMACS, etc.

- **Ejemplo:**
  ```json
  {
    "id": "b6dbf8c3-7285-4e22-ab74-a37e63bc37a0",
    "version_number": 1,
    "status": "published",
    "snapshot": {
      "int_to_uuid": {
        "1": "03f0e000-d45f-46ad-92a1-9f2b89d88415",
        "2": "fae4bddf-cfb5-43d7-b273-e073555a123a"
      },
      "uuid_to_int": {
        "03f0e000-d45f-46ad-92a1-9f2b89d88415": 1,
        "fae4bddf-cfb5-43d7-b273-e073555a123a": 2
      }
    },
    "created_at": "2025-12-05T07:49:13.483670"
  }
  ```

### 3. `tree` - Estructura Jerárquica Completa 🌳

Este es el núcleo de la respuesta. Es un objeto recursivo donde cada nodo representa una _feature_.

- **Propósito:**

  - Renderizar el árbol visual del modelo.
  - Navegar por la jerarquía (padres e hijos).
  - Identificar tipos de features (obligatorias, opcionales, abstractas).
  - Acceder a recursos educativos asociados a cada nodo.

- **Estructura de cada nodo:**

  - `id` (UUID): Identificador único de la feature
  - `name` (string): Nombre descriptivo de la feature
  - `type` (enum): Tipo de feature: `"mandatory"` (obligatoria) o `"optional"` (opcional)
  - `properties` (object): Propiedades personalizadas (horas, créditos, temas, etc.)
  - `resource` (object | null): Recurso educativo asociado
    - `id` (UUID): ID del recurso
    - `title` (string): Título del recurso
    - `type` (enum): Tipo: `"video"`, `"pdf"`, `"quiz"`, `"external_link"`, etc.
    - `content_url_or_data` (string): URL o contenido del recurso
    - `language` (string): Idioma del recurso
    - `status` (enum): Estado: `"draft"`, `"published"`, etc.
    - `duration_minutes` (int | null): Duración estimada
  - `tags` (array): Lista de etiquetas/tags asociadas
  - `group` (object | null): Información del grupo si la feature es padre de un grupo
    - `id` (UUID): ID del grupo
    - `group_type` (enum): Tipo: `"alternative"` (XOR) o `"or"`
    - `min_cardinality` (int): Mínimo de hijos a seleccionar
    - `max_cardinality` (int): Máximo de hijos a seleccionar
    - `description` (string): Descripción legible (ej: "Debes elegir EXACTAMENTE UNA opción")
  - `children` (array): Lista recursiva de nodos hijos
  - `depth` (int): Profundidad en el árbol (root = 0)
  - `is_leaf` (boolean): Indica si es nodo hoja (sin hijos)

- **Ejemplo de nodo:**
  ```json
  {
    "id": "fae4bddf-cfb5-43d7-b273-e073555a123a",
    "name": "Fundamentos de Gestión de Proyectos",
    "type": "mandatory",
    "properties": {
      "horas": 24,
      "creditos": 1.5,
      "description": "Conceptos básicos y marcos de referencia"
    },
    "resource": null,
    "tags": [],
    "group": null,
    "children": [
      {
        "id": "228aea7f-1693-42ef-ba24-fcd0259c6231",
        "name": "Introducción a Proyectos",
        "type": "mandatory",
        "properties": {
          "horas": 6,
          "temas": ["Definición de proyecto", "Ciclo de vida"]
        },
        "resource": null,
        "tags": [],
        "group": null,
        "children": [],
        "depth": 2,
        "is_leaf": true
      }
    ],
    "depth": 1,
    "is_leaf": false
  }
  ```

### 4. `relations` - Relaciones entre Features 🔗

Un array que define las interdependencias lógicas entre diferentes features del árbol.

- **Tipos de relaciones:**

  - `requires`: Dependencia directa. (Ej: _Feature A_ necesita _Feature B_).
  - `excludes`: Exclusión mutua. (Ej: _Feature A_ es incompatible con _Feature B_).

- **Propósito:**

  - Validar la configuración seleccionada por el usuario.
  - Visualizar dependencias (ej. flechas entre nodos).
  - Implementar reglas de negocio ("No puedes elegir X sin Y").

- **Estructura de cada relación:**

  - `id` (UUID): Identificador único de la relación
  - `type` (enum): Tipo de relación: `"requires"` o `"excludes"`
  - `source_feature_id` (UUID): ID de la feature origen
  - `source_feature_name` (string): Nombre de la feature origen
  - `target_feature_id` (UUID): ID de la feature destino
  - `target_feature_name` (string): Nombre de la feature destino
  - `description` (string): Descripción legible generada automáticamente

- **Semántica:**

  - **REQUIRES:** Si se selecciona `source`, entonces `target` DEBE estar seleccionado
    - Ejemplo: "Planificación y Estimación requiere Fundamentos de Gestión de Proyectos"
  - **EXCLUDES:** Si se selecciona `source`, entonces `target` NO PUEDE estar seleccionado (y viceversa)
    - Ejemplo: "Estimación Algorítmica excluye Estimación Ágil"

- **Ejemplo:**
  ```json
  [
    {
      "id": "048182b6-894e-4333-bf8e-53459512c500",
      "type": "requires",
      "source_feature_id": "1c43440d-8172-411d-9ed4-c48acd58ace2",
      "source_feature_name": "Planificación y Estimación",
      "target_feature_id": "fae4bddf-cfb5-43d7-b273-e073555a123a",
      "target_feature_name": "Fundamentos de Gestión de Proyectos",
      "description": "Planificación y Estimación requiere Fundamentos de Gestión de Proyectos"
    },
    {
      "id": "8319d65e-57cc-4d68-9cd1-8172e085d165",
      "type": "excludes",
      "source_feature_id": "96977c51-51d3-4f5f-911c-e035f73541d3",
      "source_feature_name": "Estimación Algorítmica",
      "target_feature_id": "15722f88-a481-4792-9f02-e130eb3f8cdd",
      "target_feature_name": "Estimación Ágil",
      "description": "Estimación Algorítmica excluye Estimación Ágil"
    }
  ]
  ```

### 5. `constraints` - Restricciones Formales 📐

Array para lógica proposicional compleja que no puede expresarse con relaciones simples.

- **Propósito:** Expresar reglas lógicas complejas que involucran múltiples features.

- **Casos de uso:**

  - "Debes elegir (A y B) o (C y D), pero no ambos grupos"
  - "Si seleccionas A, entonces debes elegir al menos 2 de {B, C, D}"
  - "Feature X requiere exactamente uno de {Y, Z}"

- **Estructura de cada constraint:**

  - `id` (UUID): Identificador único del constraint
  - `name` (string): Nombre descriptivo del constraint
  - `expression` (string): Expresión lógica formal (sintaxis específica del proyecto)
  - `description` (string | null): Explicación en lenguaje natural

- **Uso en validación:**

  - Fundamental para solucionadores SAT (Boolean satisfiability problem)
  - Permite validar configuraciones complejas automáticamente
  - Se convierte a formato DIMACS para análisis

- **Ejemplo:**

  ```json
  [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Metodología Exclusiva",
      "expression": "(Scrum OR Kanban OR XP) AND NOT (Scrum AND Kanban)",
      "description": "Debes elegir al menos una metodología ágil, pero no más de una al mismo tiempo"
    }
  ]
  ```

- **Nota:** En el ejemplo proporcionado, el array está vacío `[]`, lo que significa que no hay constraints adicionales más allá de las relaciones `requires`/`excludes` definidas.

### 6. `statistics` - Estadísticas del Modelo 📊

Resumen cuantitativo pre-calculado de la estructura del modelo.

- **Propósito:**

  - **Dashboard:** Visualización de métricas clave sin necesidad de recorrer el árbol
  - **Análisis:** Detección de modelos excesivamente profundos o complejos
  - **Performance:** Estimación de tiempos de carga o procesamiento
  - **UX:** Mostrar complejidad del modelo al usuario antes de explorarlo

- **Métricas incluidas:**

  - `total_features` (int): Número total de features en el modelo
  - `mandatory_features` (int): Features de tipo `"mandatory"` (obligatorias)
  - `optional_features` (int): Features de tipo `"optional"` (opcionales)
  - `total_groups` (int): Número total de grupos (XOR + OR)
  - `xor_groups` (int): Grupos de tipo `"alternative"` (elegir exactamente uno)
  - `or_groups` (int): Grupos de tipo `"or"` (elegir uno o más)
  - `total_relations` (int): Número total de relaciones entre features
  - `requires_relations` (int): Relaciones de tipo `"requires"`
  - `excludes_relations` (int): Relaciones de tipo `"excludes"`
  - `total_constraints` (int): Número de constraints formales
  - `total_configurations` (int): Configuraciones guardadas para este modelo
  - `max_tree_depth` (int): Profundidad máxima del árbol (root = 0)

- **Interpretación:**

  - **Complejidad baja:** < 50 features, depth < 5
  - **Complejidad media:** 50-200 features, depth 5-8
  - **Complejidad alta:** > 200 features, depth > 8

- **Ejemplo:**

  ```json
  {
    "total_features": 84,
    "mandatory_features": 66,
    "optional_features": 18,
    "total_groups": 5,
    "xor_groups": 1,
    "or_groups": 4,
    "total_relations": 53,
    "requires_relations": 51,
    "excludes_relations": 2,
    "total_constraints": 0,
    "total_configurations": 0,
    "max_tree_depth": 4
  }
  ```

- **Insights del ejemplo:**
  - Modelo de tamaño mediano (84 features)
  - Alta rigidez (78.6% features obligatorias)
  - Profundidad moderada (4 niveles)
  - 51 dependencias, 2 exclusiones (estructura bien conectada)

### 7. `metadata` - Metadatos de la Respuesta ⚙️

Información técnica sobre la generación y estado de la respuesta.

- **Propósito:**

  - **Debugging:** Identificación de problemas de caché o versiones
  - **Performance:** Monitoreo de latencia en la generación de datos
  - **UX:** Indicadores de frescura de datos (ej. "Actualizado hace 2 minutos")
  - **Caché:** Decisiones de invalidación y actualización

- **Campos:**

  - `cached` (boolean): Indica si la respuesta proviene del caché
  - `cache_expires_at` (datetime | null): Fecha de expiración del caché
  - `generated_at` (datetime): Timestamp de generación de la respuesta
  - `processing_time_ms` (int): Tiempo de procesamiento en milisegundos
  - `version_status` (enum): Estado de la versión: `"draft"`, `"in_review"`, `"published"`, `"archived"`

- **Estrategia de caché:**

  - **PUBLISHED:** Caché de 1 hora (datos inmutables)
  - **IN_REVIEW:** Caché de 30 minutos (cambios poco frecuentes)
  - **DRAFT:** Caché de 5 minutos (cambios frecuentes)
  - **ARCHIVED:** Caché de 1 hora (datos históricos)

- **Ejemplo:**

  ```json
  {
    "cached": false,
    "cache_expires_at": "2025-12-11T04:19:22.466353",
    "generated_at": "2025-12-11T03:19:22.466366",
    "processing_time_ms": 3,
    "version_status": "published"
  }
  ```

- **Interpretación del ejemplo:**
  - Respuesta generada en tiempo real (no caché)
  - Muy rápida: 3ms (excelente performance)
  - Versión publicada (datos estables)
  - Caché válido por 1 hora

---

## 🎯 Casos de Uso por Sección

Dependiendo del componente de la aplicación que consuma este endpoint, se utilizarán diferentes secciones:

| Componente                                 | Secciones Utilizadas                     |
| :----------------------------------------- | :--------------------------------------- |
| **Frontend - Visualizador de Árbol**       | `tree`, `statistics`, `metadata`         |
| **Frontend - Configurador de Estudiante**  | `tree`, `relations`, `constraints`       |
| **Frontend - Dashboard Administrativo**    | `feature_model`, `version`, `statistics` |
| **Backend - Generador de Configuraciones** | `tree`, `relations`, `constraints`       |

---

## 📦 Resumen de Valores Clave

Referencia rápida de los campos de nivel superior:

| Campo           | Descripción                 | Caso de Uso Principal               |
| :-------------- | :-------------------------- | :---------------------------------- |
| `feature_model` | Información del modelo base | Contexto general, breadcrumbs       |
| `version`       | Información de la versión   | Versionado, historial               |
| `tree`          | Estructura jerárquica       | Renderizado del árbol visual        |
| `relations`     | Dependencias/exclusiones    | Validación de reglas simples        |
| `constraints`   | Reglas formales             | Validación lógica avanzada          |
| `statistics`    | Métricas del modelo         | Dashboards, análisis de complejidad |
| `metadata`      | Info de la respuesta        | Debugging, control de caché         |
