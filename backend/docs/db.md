

# 🏛️ Arquitectura y Filosofía de la Plataforma

Nuestra plataforma es una poderosa **"Cocina Pedagógica"** donde los educadores pueden diseñar, construir y personalizar itinerarios de aprendizaje. Esta arquitectura nos permite pasar de un modelo rígido de "talla única" a uno flexible y adaptativo.

## 📈 Desglose de la Lógica de Negocio

El flujo de trabajo sigue un proceso lógico y colaborativo, similar a la creación de una receta gourmet:

1.  **El Dominio 📂 (`Domain`):** Todo comienza en una "cocina" o área de conocimiento, como "Ciencias" o "Humanidades".
2.  **La Receta Maestra 📜 (`FeatureModel`):** Un **Diseñador** (`MODEL_DESIGNER`) crea una plantilla maestra, la "receta" base con todos los ingredientes y pasos posibles para un curso o grado. Esta receta tiene un dueño y puede tener colaboradores (`MODEL_EDITOR`).
3.  **Los Ingredientes y Pasos 🧱 (`Feature`):** La receta se desglosa en componentes: módulos, lecciones, actividades. Estos se organizan jerárquicamente.
4.  **Las Reglas de Cocina 🔀🔗 (`FeatureGroup` & `FeatureRelation`):** Se establecen reglas: "Elige solo uno de estos postres" (Grupo `XOR`), "Necesitas cocinar las verduras antes de añadir la salsa" (Relación `REQUIRES`).
5.  **El Contenido Real 📚 (`Resource`):** Cada paso se enriquece con contenido tangible: un video, un PDF, un quiz. Estos recursos son reutilizables en múltiples recetas.
6.  **Las Etiquetas Descriptivas 🏷️ (`Tag`):** A los ingredientes y a la receta final se les añaden etiquetas como "Para principiantes", "Visual", "Práctico" para facilitar la búsqueda y la personalización.
7.  **El Visto Bueno del Chef ✅ (`REVIEWER`):** Una vez que la receta está lista (`FeatureModelVersion` en `IN_REVIEW`), un revisor la prueba y le da el sello de aprobación, publicándola (`PUBLISHED`).
8.  **El Plato Servido 🎓 (`Configuration`):** Finalmente, un **Configurador** (`CONFIGURATOR`) toma la receta aprobada y prepara un "plato" específico: un itinerario de aprendizaje a medida para un grupo o individuo.

---

## 📋 Resumen de Cada Tabla: El ADN del Aprendizaje

Aquí se detalla el propósito de cada tabla que conforma la arquitectura de nuestra plataforma.

### 👤 Tabla `User`
*   **🎯 Propósito Principal:** Gestionar la **identidad, autenticación y permisos** de cada persona que interactúa con el sistema. Es la puerta de entrada a la plataforma.
*   **🔑 Clave Educativa:** El campo `role` define qué puede ver y hacer cada usuario, separando claramente las responsabilidades entre quienes diseñan el currículo, quienes lo aprueban y quienes lo consumen.

### 📂 Tabla `Domain`
*   **🎯 Propósito Principal:** Actuar como un **contenedor de alto nivel** para organizar los `FeatureModel` por área de conocimiento, facultad o departamento.
*   **🔑 Clave Educativa:** Evita el caos al permitir una clasificación lógica de la oferta académica (ej: "Ingeniería", "Artes", "Formación Corporativa").

### 📜 Tabla `FeatureModel`
*   **🎯 Propósito Principal:** Representar la **plantilla curricular maestra** de un curso, grado o plan de formación. Es el "lienzo" donde se define todo el espacio de posibilidades pedagógicas.
*   **🔑 Clave Educativa:** El `owner_id` establece la propiedad y responsabilidad del diseño. Su relación con `FeatureModelCollaborator` habilita el trabajo en equipo entre docentes.

### 📸 Tabla `FeatureModelVersion`
*   **🎯 Propósito Principal:** Guardar una **"foto" inmutable (snapshot)** de un `FeatureModel` en un momento específico. Todo el diseño (features, reglas, etc.) se asocia a una versión.
*   **🔑 Clave Educativa:** El campo `status` (`DRAFT`, `IN_REVIEW`, `PUBLISHED`) es el motor del **flujo de trabajo de aprobación académica**. Permite evolucionar los planes de estudio sin afectar a los estudiantes que cursan versiones anteriores.

### 🧱 Tabla `Feature`
*   **🎯 Propósito Principal:** Es la **unidad mínima de aprendizaje**: un módulo, una lección, una actividad práctica, un examen.
*   **🔑 Clave Educativa:** Su naturaleza jerárquica (`parent_id`) crea la estructura del curso (Semestre > Asignatura > Tema > Lección). Su enlace a `Resource` (`resource_id`) lo conecta con el material de estudio real.

### 🔀 Tabla `FeatureGroup`
*   **🎯 Propósito Principal:** Definir **puntos de decisión pedagógica** para un conjunto de `Features` hijas.
*   **🔑 Clave Educativa:** Permite crear itinerarios flexibles: **`XOR`** para especializaciones o menciones (elige solo una), y **`OR`** para actividades o recursos opcionales.

### 🔗 Tabla `FeatureRelation`
*   **🎯 Propósito Principal:** Establecer **prerrequisitos y secuencias de aprendizaje** entre dos `Features` cualesquiera.
*   **🔑 Clave Educativa:** Modela la lógica académica fundamental (`REQUIRES`: "Para cursar 'Cálculo II', se requiere 'Cálculo I'") y las incompatibilidades (`EXCLUDES`).

### 🎓 Tabla `Configuration`
*   **🎯 Propósito Principal:** Representar el **itinerario de aprendizaje final y concreto**: un plan de estudios personalizado, un curso a medida, o la ruta formativa de un empleado.
*   **🔑 Clave Educativa:** Es la **solución** tangible generada a partir de un `FeatureModel`. Es el plan de estudios que un estudiante seguirá.

### 📚 Tabla `Resource` (Biblioteca de Objetos de Aprendizaje)
*   **🎯 Propósito Principal:** Funcionar como un **catálogo centralizado de contenido educativo reutilizable** (videos, lecturas, simulaciones, quizzes).
*   **🔑 Clave Educativa:** **Separa la estructura curricular del material de estudio.** Un video explicativo sobre la "Célula" puede ser reutilizado en cursos de Biología, Química y Medicina. Sus metadatos (`status`, `license`, `language`) permiten una gestión profesional de los activos de aprendizaje.

### 🏷️ Tabla `Tag` (Etiquetas Pedagógicas)
*   **🎯 Propósito Principal:** Proporcionar **metadatos semánticos** para clasificar y encontrar contenido según criterios pedagógicos.
*   **🔑 Clave Educativa:** Es la base para el **aprendizaje adaptativo**. Permite etiquetar `Features` y `Resources` por "Nivel de Dificultad" (Básico, Avanzado), "Estilo de Aprendizaje" (Visual, Práctico), o "Competencia" (Pensamiento Crítico, Colaboración).

### 🖇️ Tablas de Asociación (`*Link`, `*Collaborator`)
*   **🎯 Propósito Principal:** Actuar como el **"pegamento" técnico** que conecta las tablas en relaciones complejas de muchos-a-muchos.
*   **🔑 Clave Educativa:** Hacen posibles las funcionalidades clave: la colaboración en equipo, la composición de los itinerarios y el etiquetado múltiple.

---

# 💡 7 Analogías para Dominar el Sistema


creame analogias como estas, o  que sean parecidas asi, dedicadas a la educacion


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


### Analogía 5: El Planificador de Currículos Escolares 🏫

Piensa en el sistema como la herramienta que utiliza un jefe de estudios o un comité pedagógico para diseñar el plan de estudios anual de un colegio.

*   **`Domain`**: El **Nivel Educativo** (ej: "Educación Primaria", "Educación Secundaria Obligatoria").

*   **`FeatureModel`**: La **plantilla curricular completa para un curso y asignatura** (ej: "Plan Anual de Matemáticas para 5º Grado"). Define todas las unidades, temas y competencias a cubrir.

*   **`Feature`**:
    *   **Jerarquía**: Un **Trimestre**, una **Unidad Didáctica** o una **Lección Específica**. Por ejemplo, `1er Trimestre` es padre de la unidad `Números y Operaciones`, que a su vez es padre de la lección `División con dos cifras`.
    *   **Tipo**:
        *   La unidad `Geometría Plana` es **obligatoria (`mandatory`)**.
        *   Una unidad de `Introducción a la Probabilidad` podría ser **opcional (`optional`)** o de refuerzo.
        *   Al final de una unidad, se puede ofrecer la elección entre un `Examen Escrito` o un `Proyecto en Grupo` como evaluación, siendo un grupo **alternativo (`XOR`)**.

*   **`FeatureRelation`**: La **secuencia lógica de contenidos**. La lección `Resolución de Ecuaciones` (`source`) **requiere (`requires`)** haber completado la lección `Operaciones con Polinomios` (`target`).

*   **`Configuration`**: El **plan de clases real de un profesor para el año escolar**. Por ejemplo, "Programación de aula del Profesor García para 5ºB", que puede adaptar el ritmo o incluir actividades opcionales según las necesidades de su clase.

*   **`Configuration_Feature`**: La **lista secuencial y detallada de lecciones y evaluaciones** que el Profesor García impartirá durante el año.

---

### Analogía 6: El Diseñador de Rutas de Aprendizaje de Idiomas 🗺️

Imagina que eres el diseñador de una aplicación como Duolingo o Babbel, creando el camino completo para que un estudiante domine un nuevo idioma.

*   **`Domain`**: El **Idioma a aprender** (ej: "Inglés", "Francés", "Alemán").

*   **`FeatureModel`**: El **"Árbol de Habilidades" completo del idioma** (ej: "Ruta de Aprendizaje: de Cero a B2 en Inglés"). Contiene todos los niveles, habilidades y lecciones.

*   **`Feature`**:
    *   **Jerarquía**: Un **Nivel del MCER**, una **Habilidad** o una **Micro-lección**. Por ejemplo, el nivel `A2 (Elemental)` es padre de las habilidades `Gramática`, `Vocabulario` y `Comprensión Auditiva`. `Gramática` es padre de lecciones como `El Pasado Simple` y `Los Comparativos`.
    *   **Tipo**:
        *   La lección `Verbo 'To Be'` es **obligatoria (`mandatory`)**.
        *   Un módulo de `Inglés de Negocios` es **opcional (`optional`)**.
        *   Se podría ofrecer una especialización en `Inglés Americano` vs. `Inglés Británico`, siendo una elección **alternativa (`XOR`)**.

*   **`FeatureRelation`**: La **progresión gramatical**. La lección `Pasado Perfecto` (`source`) **requiere (`requires`)** tener dominada la lección `Pasado Simple` (`target`).

*   **`Configuration`**: El **plan de estudio personalizado para un usuario específico**. Por ejemplo, "Plan de María para su viaje a Londres", que prioriza las lecciones de vocabulario de viajes y comprensión auditiva.

*   **`Configuration_Feature`**: El **conjunto exacto de micro-lecciones y ejercicios** que la aplicación presenta a María en su ruta de aprendizaje.

---

### Analogía 7: El Arquitecto de Certificaciones Profesionales 🛠️

Visualiza el sistema como la herramienta de un instituto de formación profesional para diseñar programas que otorgan certificaciones basadas en competencias prácticas y teóricas.

*   **`Domain`**: El **Área Profesional** (ej: "Electricidad Industrial", "Desarrollo Web Full-Stack", "Gastronomía").

*   **`FeatureModel`**: El **itinerario completo para una certificación** (ej: "Certificación Oficial en Soldadura TIG"). Define todos los módulos teóricos, prácticos y de seguridad.

*   **`Feature`**:
    *   **Jerarquía**: Un **Módulo Teórico**, una **Competencia Práctica** o una **Sesión de Taller**. El módulo `Seguridad en el Taller` es padre de la lección `Uso de Equipo de Protección Individual (EPI)`. El módulo `Técnicas de Soldadura` es padre de la competencia `Soldadura en posición vertical`.
    *   **Tipo**:
        *   El módulo `Seguridad en el Taller` es **obligatorio (`mandatory`)**.
        *   Un taller sobre `Soldadura de Materiales Exóticos` es **opcional (`optional`)**.
        *   El proyecto final puede ser un `Examen Práctico Supervisado` o la `Presentación de un Portfolio de Proyectos`, siendo una elección **alternativa (`XOR`)**.

*   **`FeatureRelation`**: La **dependencia entre teoría y práctica**. La competencia práctica `Realizar soldadura en techo` (`source`) **requiere (`requires`)** haber aprobado el módulo teórico `Fundamentos de la Metalurgia` (`target`).

*   **`Configuration`**: El **expediente formativo de un aprendiz**. Por ejemplo, "Plan de Formación de Carlos", que podría convalidar módulos si ya tiene una certificación previa en un área relacionada.

*   **`Configuration_Feature`**: La **lista de todos los módulos, prácticas de taller y evaluaciones** que Carlos debe completar para obtener su certificación.