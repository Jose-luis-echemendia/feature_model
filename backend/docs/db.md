
### 1. Objetivo Principal del Sistema

El objetivo es crear una plataforma para **modelar, configurar y gestionar Líneas de Producto de --- (Software Product Lines - SPL)** en el ámbito educativo.



### 2. ### Desglose de la Lógica de Negocio y su Propósito. Resumen de Cada Tabla (Esquema Actual)

Aquí tienes una descripción de cada tabla y su propósito en tu sistema.

#### **Tabla `User`**
*   **Objetivo Principal:** Gestionar la identidad y los permisos de las personas que usan la aplicación.
*   **Propósito:** Es la tabla de autenticación y autorización. Define quién puede entrar y qué puede hacer (crear modelos, crear configuraciones, etc.). El campo `role` es clave para diferenciar entre un profesor y un alumno.

#### **Tabla `Domain`**
*   **Objetivo Principal:** Agrupar `FeatureModels` por área de conocimiento o materia.
*   **Propósito:** Sirve como una carpeta de alto nivel. Permite organizar el contenido, por ejemplo, "Matemáticas", "Historia", "Diseño de Videojuegos". Sin ella, todos los modelos estarían en una única lista, lo cual sería caótico.

#### **Tabla `FeatureModel`**
*   **Objetivo Principal:** Definir la plantilla o el "problema" a resolver. Es el concepto central que un profesor crea.
*   **Propósito:** Representa un ejercicio o proyecto específico, como "Diseñar un Coche Eléctrico" o "Configurar un Ordenador". Contiene el nombre y la descripción general del problema. Es el padre de todas sus versiones.

#### **Tabla `FeatureModelVersion`**
*   **Objetivo Principal:** Guardar una "foto" inmutable de un `FeatureModel` en un momento dado.
*   **Propósito:** Es crucial. Permite que un profesor pueda mejorar o cambiar un modelo (`v2`, `v3`) sin afectar las tareas que ya están en curso usando una versión anterior (`v1`). Todos los componentes del modelo (`Features`, `Relations`, `Constraints`) se asocian a una versión específica, no al modelo general.

#### **Tabla `Feature`**
*   **Objetivo Principal:** Representar una característica, opción o componente individual que un usuario puede seleccionar.
*   **Propósito:** Son los "bloques de construcción" del modelo. Cada `Feature` puede ser obligatoria, opcional, etc. La estructura jerárquica (`parent_id`) crea el árbol de características, que es la visualización principal del modelo.

#### **Tabla `FeatureGroup`**
*   **Objetivo Principal:** Definir relaciones de variabilidad entre un grupo de `Features` hijas.
*   **Propósito:** Impone reglas sobre cómo se pueden elegir las características hijas de un mismo padre.
    *   **XOR (`group_type`):** "Elige solo una de estas opciones" (Ej: Tipo de motor: Gasolina, Diésel, Eléctrico).
    *   **OR (`group_type`):** "Elige una o más de estas opciones" (Ej: Extras del coche: GPS, Techo solar, Asientos de cuero).

#### **Tabla `FeatureRelation`**
*   **Objetivo Principal:** Definir restricciones entre dos `Features` cualesquiera en el árbol, sin importar dónde estén.
*   **Propósito:** Modela dependencias complejas.
    *   **Requires (`type`):** "Si eliges A, estás obligado a elegir B" (Ej: "Elegir 'Modo Turbo' requiere 'Motor de Alto Rendimiento'").
    *   **Excludes (`type`):** "Si eliges A, no puedes elegir B" (Ej: "Elegir 'Transmisión Manual' excluye 'Control de Crucero Adaptativo'").

#### **Tabla `Constraint`**
*   **Objetivo Principal:** Definir reglas complejas que no se pueden expresar fácilmente con `FeatureRelation`.
*   **Propósito:** Es una vía de escape para lógica muy avanzada, escrita en un formato textual (`expr_text`). Por ejemplo: "(FeatureA y FeatureB) -> FeatureC". Para un contexto educativo, es posible que no la uses mucho al principio, pero es bueno tenerla para casos avanzados.

#### **Tabla `Configuration`**
*   **Objetivo Principal:** Almacenar una selección de `Features` hecha por un usuario que es válida según las reglas del `FeatureModelVersion`.
*   **Propósito:** Es la **solución del alumno**. Representa el "animal diseñado", el "coche configurado" o la "respuesta" al problema planteado por el profesor. Es el artefacto principal que se crearía, guardaría y, con las mejoras sugeridas, se evaluaría.

#### **Tabla `ConfigurationFeatureLink`**
*   **Objetivo Principal:** Conectar una `Configuration` con todas las `Features` que fueron seleccionadas en ella.
*   **Propósito:** Es una tabla de unión técnica para implementar la relación muchos-a-muchos entre configuraciones y características. Una configuración tiene muchas características, y una característica puede estar en muchas configuraciones diferentes.




### Analogías para Entenderlo Mejor


### Analogía 1: El Arquitecto de Grados Universitarios

Piensa en tu sistema como la herramienta que usa el decano de una facultad para diseñar y adaptar los planes de estudio de toda la universidad.

*   **`Domain`**: La **Facultad o Escuela** (ej: "Facultad de Ingeniería", "Escuela de Artes y Humanidades"). Es el contenedor de nivel más alto.

*   **`FeatureModel`**: La **plantilla maestra de un Grado o Carrera** (ej: "Grado en Ingeniería Informática"). Define la estructura completa y todas las asignaturas y caminos posibles.

*   **`Feature`**:
    *   **Jerarquía**: Una **Asignatura** o un **Semestre**. Por ejemplo, la feature `Semestre 1` es padre de las features `Cálculo I`, `Álgebra Lineal` y `Fundamentos de Programación`.
    *   **Tipo**:
        *   `Cálculo I` es **obligatoria (`mandatory`)**.
        *   `Robótica Avanzada` es **opcional (`optional`)**.
        *   Las asignaturas de una mención o especialización (ej: "Inteligencia Artificial" vs. "Ciberseguridad") son parte de un grupo **alternativo (`XOR`)**: debes elegir una rama, no ambas.

*   **`FeatureRelation`**: Los **prerrequisitos académicos**. La asignatura `Cálculo II` (`source`) **requiere (`requires`)** haber cursado `Cálculo I` (`target`).

*   **`Configuration`**: Un **Plan de Estudios Específico y Válido**. Puede ser el "Plan recomendado para la Mención en Inteligencia Artificial 2024" o el "Expediente Académico Personalizado de la alumna Sofía Pérez".

*   **`Configuration_Feature`**: La **lista final de asignaturas** que componen ese plan de estudios específico.

---

### Analogía 2: El Constructor de Cursos Online (Estilo MOOC)

Imagina que eres un creador de cursos para una plataforma como Coursera o edX. Tu sistema es la herramienta de autor para ensamblar cursos flexibles.

*   **`Domain`**: La **Categoría General del Curso** (ej: "Desarrollo de Software", "Marketing Digital").

*   **`FeatureModel`**: El **curso maestro completo** (ej: "Curso Definitivo de Python: de Principiante a Experto"). Contiene todos los módulos y recursos posibles que podrías ofrecer.

*   **`Feature`**:
    *   **Jerarquía**: Un **Módulo**, una **Lección** o un **Recurso**. El módulo `Estructuras de Datos` es padre de las lecciones `Listas y Tuplas` y `Diccionarios`. La lección `Listas y Tuplas` es padre de los recursos `Video Explicativo` y `Cuaderno de Jupyter`.
    *   **Tipo**:
        *   El `Módulo 1: Introducción` es **obligatorio (`mandatory`)**.
        *   El `Módulo 7: Tópicos Avanzados` es **opcional (`optional`)**.
        *   El tipo de proyecto final (ej: "Análisis de Datos" vs. "Aplicación Web") es **alternativo (`XOR`)**.

*   **`FeatureRelation`**: La **secuencia de aprendizaje lógica**. La lección `Programación Orientada a Objetos` (`source`) **requiere (`requires`)** haber completado la lección `Funciones y Métodos` (`target`).

*   **`Configuration`**: Una **versión específica del curso para un público objetivo**. Por ejemplo, "Curso de Python para Analistas de Datos", que incluye los módulos básicos, los de análisis de datos y el proyecto de datos, pero omite los módulos de desarrollo web.

*   **`Configuration_Feature`**: El **conjunto exacto de lecciones y recursos** que se incluyen en esa versión del curso.

---

### Analogía 3: El Diseñador de Planes de Formación Corporativa

Visualiza tu sistema como la herramienta del departamento de Recursos Humanos para crear planes de desarrollo y onboarding para los empleados de una empresa.

*   **`Domain`**: El **Departamento o Área Funcional** (ej: "Ventas", "Operaciones", "Tecnología").

*   **`FeatureModel`**: El **Programa de Desarrollo Profesional completo** (ej: "Plan de Carrera para Ingeniero de Software").

*   **`Feature`**:
    *   **Jerarquía**: Una **Competencia**, una **Habilidad** o una **Actividad de Formación**. La competencia `Liderazgo` es padre de las habilidades `Comunicación Efectiva` y `Gestión de Proyectos`. `Comunicación Efectiva` es padre de las actividades `Curso de Oratoria` y `Taller de Feedback`.
    *   **Tipo**:
        *   El curso `Seguridad de la Información` es **obligatorio (`mandatory`)** para todos.
        *   Un `Curso de Idiomas` es **opcional (`optional`)**.
        *   La ruta de formación (ej: `Ruta Técnica` vs. `Ruta de Gestión`) es **alternativa (`XOR`)**.

*   **`FeatureRelation`**: Los **niveles de competencia**. El taller `Gestión de Proyectos Avanzada` (`source`) **requiere (`requires`)** haber completado el curso `Introducción a Metodologías Ágiles` (`target`).

*   **`Configuration`**: El **Plan de Formación Personalizado para un Empleado**. Por ejemplo, "Plan de Onboarding de 90 días para David, Ingeniero Junior" o "Plan de Desarrollo 2025 para Laura, futura Jefa de Equipo".

*   **`Configuration_Feature`**: La **lista concreta de cursos, talleres y mentorías** asignadas a ese empleado para un período determinado.

---

### Analogía 4: El Chef de Itinerarios de Aprendizaje Personalizados

Imagina que eres un "chef pedagógico" que crea "recetas de aprendizaje" a medida para cada estudiante, adaptándose a sus necesidades y gustos.

*   **`Domain`**: La **Materia o Área de Estudio** (ej: "Álgebra", "Historia del Arte").

*   **`FeatureModel`**: El **Libro de Recetas Maestro** para un objetivo de aprendizaje (ej: "Dominar la Fotosíntesis"). Contiene todos los "ingredientes" y "pasos" posibles.

*   **`Feature`**:
    *   **Jerarquía**: Un **Concepto Clave**, un **Tipo de Contenido** o una **Actividad Práctica**. El concepto `Fase Luminosa` es padre de los tipos de contenido `Explicación en Video`, `Lectura de Texto` e `Infografía Interactiva`.
    *   **Tipo**:
        *   `Concepto: Cloroplastos` es un ingrediente **obligatorio (`mandatory`)**.
        *   `Actividad: Experimento en Casa` es **opcional (`optional`)**.
        *   El formato de evaluación final (`Examen Tipo Test` vs. `Ensayo Escrito`) es **alternativo (`XOR`)**, adaptándose al estilo del estudiante.

*   **`FeatureRelation`**: Las **reglas de la cocina pedagógica**. La actividad `Resolver Problemas Complejos` (`source`) **requiere (`requires`)** el contenido `Teoría Fundamental` (`target`). No puedes cocinar el plato principal sin los ingredientes base.

*   **`Configuration`**: La **Receta de Aprendizaje a Medida** para un estudiante. Por ejemplo, "Plan de estudio sobre la Fotosíntesis para Alex, que prefiere aprender con videos y practicar con ejercicios interactivos".

*   **`Configuration_Feature`**: La **combinación exacta de videos, lecturas y quizzes** que conforman el itinerario personalizado de Alex.



### Analogía 5: Coche

Piensa en el **configurador de un coche en una página web**:

*   **`domain`**: El tipo de vehículo (ej: "Coches", "Motos").
*   **`feature_model`**: El modelo específico (ej: "SUV Modelo X").
*   **`feature`**:
    *   **Jerarquía**: La característica `Motor` tiene hijos como `Motor a Gasolina` y `Motor Híbrido`.
    *   **Tipo**: `Motor` es `mandatory`, pero la elección entre `Gasolina` e `Híbrido` es `alternative`. `Techo solar` es `optional`.
*   **`feature_relation`**: La característica `Llantas Deportivas de 20"` (`requires`) `Suspensión Deportiva`.
*   **`configuration`**: "Mi Coche SUV Modelo X Personalizado".
*   **`configuration_feature`**: La lista final de opciones que elegiste (Motor Híbrido, Techo Solar, Llantas Deportivas, Suspensión Deportiva, etc.).





### 2. Resumen de las Tablas con la Nueva Lógica

Aquí está el "para qué" de cada tabla en tu nuevo contexto de **diseño instruccional**:

*   **`User`**:
    *   **Quién:** Diseñador Instruccional, Administrador Académico, Jefe de Formación.
    *   **Objetivo:** Gestionar quién tiene permiso para crear y modificar las plantillas de cursos.

*   **`Domain`**:
    *   **Qué:** Un área de conocimiento o facultad. (Ej: "Tecnología", "Humanidades", "Ventas").
    *   **Objetivo:** Organizar las plantillas de cursos (`FeatureModel`) en categorías lógicas.

*   **`FeatureModel`**:
    *   **Qué:** La plantilla maestra para un curso, un grado completo o un plan de formación. (Ej: "Máster en Ciberseguridad").
    *   **Objetivo:** Contener todas las posibles variantes, módulos y reglas de un programa educativo. Es el "lienzo" del diseñador.

*   **`FeatureModelVersion`**:
    *   **Qué:** Una "edición" del plan de estudios. (Ej: "Plan de Estudios 2024", "Plan de Estudios 2025").
    *   **Objetivo:** Permitir la evolución de los programas educativos (añadir/quitar módulos) sin romper los itinerarios ya generados con versiones anteriores. Esencial para la gestión académica a largo plazo.

*   **`Feature`**:
    *   **Qué:** El bloque de construcción fundamental del aprendizaje: un **módulo, una lección, una actividad, un recurso, una evaluación**.
    *   **Objetivo:** Representar cada pieza del rompecabezas educativo. El campo `metadata` aquí es **CRÍTICO**: puede contener el ID del video, el enlace a un PDF, la duración estimada, los objetivos de aprendizaje de esa lección, etc.

*   **`FeatureGroup`**:
    *   **Qué:** Reglas de selección para un conjunto de componentes educativos.
    *   **Objetivo:**
        *   **XOR:** Definir **rutas de especialización excluyentes**. (Ej: Elige la especialidad en "Frontend" O "Backend").
        *   **OR:** Ofrecer un **catálogo de actividades opcionales o complementarias**. (Ej: Elige al menos dos de estos cuatro casos de estudio).

*   **`FeatureRelation`**:
    *   **Qué:** Una dependencia directa entre dos componentes.
    *   **Objetivo:** Modelar **prerrequisitos** (`REQUIRES`) de forma explícita. (Ej: La lección "Funciones Avanzadas" requiere la lección "Fundamentos de Funciones"). También puede modelar **incompatibilidades** (`EXCLUDES`).

*   **`Constraint`**:
    *   **Qué:** Reglas pedagógicas complejas.
    *   **Objetivo:** Definir lógicas que van más allá de los prerrequisitos simples. (Ej: "Para obtener el certificado, el alumno debe completar el Proyecto Final O (el Módulo de Prácticas Y el Examen Teórico)").

*   **`Configuration`**:
    *   **Qué:** Un **plan de estudios o itinerario de aprendizaje final y concreto**. (Ej: "Plan de Estudios para el Grupo A - 2024", "Itinerario Personalizado para María García").
    *   **Objetivo:** Representar el **resultado final del proceso de diseño**: una ruta de aprendizaje válida, coherente y lista para ser "consumida" por un estudiante.

*   **`ConfigurationFeatureLink`**:
    *   **Qué:** La lista detallada de todos los módulos, lecciones y actividades que componen un itinerario específico.
    *   **Objetivo:** Conectar técnicamente el plan de estudios (`Configuration`) con sus componentes (`Feature`).

---




Tu base de datos es una base excelente para construir un **motor de personalización de aprendizaje a escala**. Permite a las instituciones educativas o empresas pasar de un modelo de "talla única para todos" a la creación masiva de "currículos a medida". ¡Es un proyecto muy potente

