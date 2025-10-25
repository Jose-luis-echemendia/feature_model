

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

# 💡 5 Analogías para Dominar el Sistema

Para comprender la arquitectura, pensemos en ella como un sistema para crear experiencias de aprendizaje asombrosas.

### 1. El Arquitecto de Grados Universitarios 🏛️
Nuestra plataforma es la herramienta del Decano para diseñar los planes de estudio de toda la facultad.

*   **`Domain` ➜ La Facultad** (ej: "Facultad de Ingeniería").
*   **`FeatureModel` ➜ La Plantilla del Grado** (ej: "Grado en Ingeniería Informática"), creada por el **Director de Carrera (`MODEL_DESIGNER`)**.
*   **`Feature` ➜ La Asignatura o el Semestre** (ej: `Cálculo I`).
*   **`FeatureRelation` ➜ Los Prerrequisitos** ("'Cálculo II' `REQUIRES` 'Cálculo I'").
*   **`Resource` ➜ El Material de Estudio** (El PDF del libro, el enlace al simulador de laboratorio).
*   **`Tag` ➜ La Clasificación Académica** ("Nivel Básico", "Requiere Habilidades Analíticas").
*   **`REVIEWER` ➜ El Comité Académico** que aprueba el plan de estudios.
*   **`Configuration` ➜ El Expediente Personalizado** de un alumno, diseñado por su **Tutor Académico (`CONFIGURATOR`)**.

### 2. El Constructor de Cursos Online (Estilo MOOC) 💻
Somos la herramienta de autor para crear cursos flexibles en plataformas como Coursera o edX.

*   **`Domain` ➜ La Categoría del Curso** (ej: "Desarrollo de Software").
*   **`FeatureModel` ➜ El Curso Maestro Completo** (ej: "Python: de Principiante a Experto"), diseñado por el **Instructor Principal (`MODEL_DESIGNER`)** y sus **Asistentes (`MODEL_EDITOR`)**.
*   **`Feature` ➜ El Módulo, la Lección o la Tarea**.
*   **`FeatureGroup` ➜ La Especialización** (`XOR`: Elige el proyecto de "Análisis de Datos" *o* "Desarrollo Web").
*   **`Resource` ➜ El Video de la Lección** (el archivo `.mp4`) o el PDF con ejercicios.
*   **`Tag` ➜ El Perfil del Contenido** ("Para Principiantes", "Video-Lección", "Evaluación").
*   **`Configuration` ➜ La Versión del Curso para un Público** (ej: "Curso de Python para Analistas de Datos").

### 3. El Diseñador de Formación Corporativa 📈
Somos la herramienta de RRHH para crear planes de desarrollo y onboarding para empleados.

*   **`Domain` ➜ El Área Funcional** (ej: "Ventas", "Tecnología").
*   **`FeatureModel` ➜ El Programa de Desarrollo Profesional** (ej: "Plan de Carrera para Ingenieros").
*   **`Feature` ➜ La Competencia o la Actividad de Formación** (ej: `Habilidad: Comunicación Efectiva`).
*   **`Resource` ➜ El Material del Taller** (el video del curso de compliance, la presentación del taller).
*   **`Tag` ➜ La Competencia Clave** ("Liderazgo", "Habilidad Blanda", "Obligatorio para Ventas").
*   **`REVIEWER` ➜ El Director de RRHH** que da el visto bueno al plan.
*   **`Configuration` ➜ El Plan de Formación Personalizado** para un empleado.

### 4. El Constructor de Kits de Aprendizaje LEGO® 🧱
Nuestra plataforma es como la fábrica de LEGO®, donde diseñamos kits educativos que otros pueden construir.

*   **`Domain` ➜ La Línea de Productos** (`LEGO® Education`, `LEGO® Mindstorms`).
*   **`FeatureModel` ➜ El Manual de Instrucciones** para un kit (ej: "Kit de Robótica Básico").
*   **`Feature` ➜ Un Tipo de Pieza o un Paso de Montaje** (un "bloque rojo 2x4", un "sensor de color").
*   **`Resource` ➜ El Diseño CAD de una Pieza Especial** que puede ser usada en múltiples kits.
*   **`FeatureRelation` ➜ Las Reglas de Ensamblaje** ("El motor debe conectarse al engranaje principal").
*   **`Tag` ➜ La Información de la Caja** ("Edades 9-14", "Nivel Experto").
*   **`Configuration` ➜ El Robot Terminado**, ensamblado por un **Estudiante (`CONFIGURATOR`)** siguiendo las instrucciones.

### 5. El Director de Orquesta Sinfónica 🎼
Somos el podio desde donde un director puede componer y adaptar una sinfonía (un curso completo).

*   **`Domain` ➜ El Período Musical** ("Barroco", "Clásico", "Romántico").
*   **`FeatureModel` ➜ La Partitura Maestra** de una sinfonía, con todas las secciones y variaciones posibles. La crea el **Compositor (`MODEL_DESIGNER`)**.
*   **`Feature` ➜ Una Sección o Instrumento** (la "Sección de Cuerdas", el "Solo de Oboe").
*   **`FeatureGroup` ➜ Variaciones de Interpretación** (`XOR`: Tocar la sección "Adagio" *o* la versión "Allegro").
*   **`Resource` ➜ La Particella de un Músico** (la hoja de música específica para el primer violín).
*   **`Tag` ➜ El Carácter de la Música** ("Enérgico", "Melancólico", "Virtuoso").
*   **`Configuration` ➜ La Interpretación en un Concierto Específico**, adaptada por el **Director (`CONFIGURATOR`)** según la acústica de la sala y la ocasión.
