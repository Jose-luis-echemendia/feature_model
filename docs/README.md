#  CuriConfig: Configurador Dinámico de Itinerarios Curriculares 🎓

![Estado del Proyecto](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Licencia](https://img.shields.io/badge/licencia-MIT-blue)

**CuriConfig** es una innovadora plataforma web diseñada para la creación y gestión de planes de estudio y formación basados en modelos de características (*feature modeling*). Este sistema transforma la manera en que las instituciones educativas y corporativas diseñan sus currículos, pasando de un modelo estático a uno dinámico, modular y personalizable.

---

## 📜 Proyecto de Tesis

Este proyecto es el resultado de nuestro trabajo de tesis para optar por el título de Ingeniería en Ciencias Informáticas.

*   **Título General del Proyecto:** "Plataforma para la Configuración de Modelos de Características Aplicada al Diseño Curricular"
*   **Promotora y Tutora General:** M. Sc. Yadira Ramírez Rodríguez (yramirezr@uci.cu)

### 👨‍💻 Tesistas y Autores

| Rol             | Autor                                   | Tesis Individual                                                                              | Contacto                                   | Tutor Específico           |
| --------------- | --------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------------- |
| 🚀 **Backend**  | José Luis Echemendía López              | _"Desarrollo de un sistema gestor de modelos de características utilizando FastAPI y PostgreSQL"_ | josee@estudiantes.uci.cu                  | M. Sc. Yadira Ramírez Rodríguez Ing. Liany Sobrino Miranda |
| 🎨 **Frontend** | Ernes [Tu Apellido] [Tu Apellido] | _"Implementación de una interfaz visual para la configuración de itinerarios curriculares con Next.js"_ | evdiaz@estudiantes.uci.cu                      | M. Sc. Yadira Ramírez Rodríguez |

---

## 📑 Tabla de Contenidos

1.  [Propósito y Objetivos](#-propósito-y-objetivos)
2.  [🌟 Características Principales](#-características-principales)
3.  [🛠️ Stack Tecnológico](#️-stack-tecnológico)
4.  [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
5.  [🚀 Guía de Instalación y Puesta en Marcha](#-guía-de-instalación-y-puesta-en-marcha)
6.  [📁 Estructura de Carpetas](#-estructura-de-carpetas)
7.  [✍️ Estándares y Convenciones de Código](#️-estándares-y-convenciones-de-código)
8.  [⚙️ Variables de Entorno](#️-variables-de-entorno)
9.  [📚 Documentación de la API](#-documentación-de-la-api)
10. [⚖️ Licencia](#️-licencia)

---

## 🎯 Propósito y Objetivos

El propósito fundamental de **CuriConfig** es ofrecer una herramienta flexible y potente para que diseñadores instruccionales, académicos y jefes de formación puedan modelar, validar y generar itinerarios de aprendizaje a medida.

### Objetivos Principales

*   **Modelado Visual:** Permitir la creación de planes de estudio como árboles de características jerárquicos y visuales.
*   **Validación Automática:** Asegurar que cualquier itinerario generado sea coherente y válido, aplicando reglas de prerrequisitos, exclusiones y opcionalidad.
*   **Reutilización de Contenido:** Centralizar los recursos de aprendizaje (videos, documentos) para que puedan ser reutilizados en múltiples cursos.
*   **Flexibilidad Curricular:** Facilitar la creación de especializaciones, rutas personalizadas y planes adaptativos para diferentes perfiles de estudiantes.
*   **Colaboración y Calidad:** Implementar un flujo de trabajo basado en roles que permita la colaboración en el diseño y la aprobación de los planes de estudio antes de su publicación.

---

## 🌟 Características Principales

*   ✅ **Diseño de Modelos:** Crea y edita visualmente los modelos de características con elementos obligatorios, opcionales, alternativos (XOR) y opcionales en grupo (OR).
*   ✅ **Gestión de Reglas:** Define relaciones complejas como prerrequisitos (`requires`) y exclusiones (`excludes`) entre componentes.
*   ✅ **Biblioteca de Recursos:** Un catálogo centralizado para gestionar los materiales de aprendizaje (`Resource`) y enlazarlos a los componentes del curso.
*   ✅ **Etiquetado Pedagógico:** Usa `Tags` para clasificar componentes por dificultad, estilo de aprendizaje o competencias, permitiendo la personalización avanzada.
*   ✅ **Control de Versiones:** Guarda "snapshots" de los modelos para poder evolucionarlos sin afectar a los itinerarios ya generados.
*   ✅ **Roles y Permisos:** Un sistema granular de roles (`ADMIN`, `MODEL_DESIGNER`, `REVIEWER`, etc.) que define un flujo de trabajo claro de creación, revisión y publicación.
*   ✅ **Generación de Configuraciones:** Ensambla itinerarios de aprendizaje válidos y listos para ser exportados o implementados.

---

## 🛠️ Stack Tecnológico

Hemos elegido un stack tecnológico moderno, robusto y escalable para dar vida a CuriConfig.

| Tecnología                                                                                                                              | Rol en el Proyecto                                                                                             |
| --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="40"/>      | **Backend Framework (API):** Construye una API RESTful de alto rendimiento, asíncrona y con documentación automática. |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" width="40"/>        | **Lenguaje del Backend:** Permite un desarrollo rápido y limpio, con un vasto ecosistema de librerías.             |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nextjs/nextjs-original.svg" alt="Next.js" width="40"/>        | **Frontend Framework:** Proporciona una experiencia de usuario fluida con renderizado del lado del servidor (SSR) y una estructura robusta sobre React. |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg" alt="React" width="40"/>            | **Librería de UI:** Permite construir interfaces de usuario interactivas y reutilizables.                        |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" alt="PostgreSQL" width="40"/> | **Base de Datos:** Un sistema de base de datos relacional potente y fiable, ideal para manejar las complejas relaciones de nuestro modelo. |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg" alt="Docker" width="40"/>          | **Contenerización:** Permite empaquetar la aplicación y sus dependencias en contenedores, garantizando un entorno de desarrollo y despliegue consistente. |

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura de microservicios desacoplada, orquestada con Docker.

```mermaid
graph TD
    A[👨‍💻 Usuario] -->|Navegador Web| B(🌐 Frontend - Next.js/React);
    B -->|Peticiones API (REST)| C(🚀 Backend - FastAPI/Python);
    C -->|Consultas SQL| D(🗄️ Base de Datos - PostgreSQL);
    C --> E{🔄 Lógica de Negocio};
    subgraph "Contenedores Docker"
        B
        C
        D
    end
```

---

## 🚀 Guía de Instalación y Puesta en Marcha

Para levantar el proyecto en tu entorno local, asegúrate de tener `Docker` y `Docker Compose` instalados.

1.  **Clona el repositorio:**
    ```bash
    git clone [URL_DE_TU_REPOSITORIO]
    cd [NOMBRE_DEL_REPOSITORIO]
    ```

2.  **Configura las variables de entorno:**
    *   En la raíz del proyecto, encontrarás los archivos `.env.example` para el backend y el frontend.
    *   Crea una copia de cada uno y renómbrala a `.env`.
        ```bash
        cp ./backend/.env.example ./backend/.env
        cp ./frontend/.env.example ./frontend/.env
        ```
    *   Revisa los archivos `.env` y ajusta las variables si es necesario (ej. `POSTGRES_PASSWORD`, `SECRET_KEY`).

3.  **Levanta los servicios con Docker Compose:**
    *   Desde la raíz del proyecto, ejecuta el siguiente comando. Esto construirá las imágenes y levantará los contenedores del frontend, backend y la base de datos.
    ```bash
    docker-compose up --build
    ```

4.  **¡Listo para usar!**
    *   🌐 **Frontend:** La aplicación estará disponible en `http://localhost:3000`.
    *   🚀 **Backend (API Docs):** La documentación interactiva de la API estará en `http://localhost:8000/docs`.

---

## 📁 Estructura de Carpetas

La estructura del proyecto está organizada para separar claramente las responsabilidades del backend y del frontend.

```
.
├── backend/               # Contiene todo el código de la API de FastAPI
│   ├── app/               # Lógica principal de la aplicación
│   │   ├── api/           # Endpoints y rutas de la API
│   │   ├── core/          # Configuración, seguridad, etc.
│   │   ├── crud/          # Operaciones CRUD con la base de datos
│   │   ├── models/        # Modelos de datos (SQLModel)
│   │   ├── schemas/       # Esquemas de datos (Pydantic)
│   │   └── enums/         # Enumeraciones
│   ├── migrations/        # Migraciones de la base de datos (Alembic)
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/              # Contiene todo el código de la UI de Next.js
│   ├── app/               # Rutas y páginas de la aplicación
│   ├── components/        # Componentes reutilizables de React
│   ├── contexts/          # Contextos de React para estado global
│   ├── services/          # Lógica para interactuar con la API
│   ├── styles/            # Estilos globales y CSS Modules
│   ├── .env.example
│   └── Dockerfile
│
└── docker-compose.yml     # Orquesta todos los servicios
```

---

## ✍️ Estándares y Convenciones de Código

Para mantener la calidad y consistencia del código, seguimos los siguientes estándares:

### Backend (Python)
*   **Formateo:** `Black` para un estilo de código unificado.
*   **Linting:** `Flake8` y `Ruff` para detectar errores y malas prácticas.
*   **Tipado:** `Mypy` para el análisis de tipos estáticos.
*   **Nomenclatura:** `snake_case` para variables y funciones.

### Frontend (TypeScript/React)
*   **Formateo:** `Prettier` para un formato de código consistente.
*   **Linting:** `ESLint` para identificar y corregir problemas en el código.
*   **Nomenclatura:** `camelCase` para variables y funciones, `PascalCase` para componentes de React.

---

## ⚙️ Variables de Entorno

A continuación se listan las variables de entorno clave necesarias para el funcionamiento del sistema.

| Variable                 | Servicio | Descripción                                                    | Ejemplo                               |
| ------------------------ | -------- | -------------------------------------------------------------- | ------------------------------------- |
| `POSTGRES_USER`          | Backend  | Usuario para la base de datos PostgreSQL.                      | `postgres`                            |
| `POSTGRES_PASSWORD`      | Backend  | Contraseña para el usuario de la BD.                           | `supersecretpassword`                 |
| `POSTGRES_DB`            | Backend  | Nombre de la base de datos.                                    | `curiconfig_db`                       |
| `DATABASE_URL`           | Backend  | URL de conexión completa a la base de datos.                   | `postgresql://user:pass@db/dbname`    |
| `SECRET_KEY`             | Backend  | Clave secreta para la generación de tokens JWT.                | `un-secreto-muy-largo-y-aleatorio`    |
| `NEXT_PUBLIC_API_URL`    | Frontend | URL base del backend para que el frontend pueda hacer peticiones. | `http://localhost:8000`               |

---

## 📚 Documentación de la API

La API de CuriConfig está auto-documentada gracias a FastAPI y el estándar OpenAPI. Una vez que el backend esté corriendo, puedes acceder a la documentación interactiva (Swagger UI) en:

➡️ **[http://localhost:8000/docs](http://localhost:8000/docs)**

Allí podrás explorar todos los endpoints, ver los esquemas de datos y probar la API directamente desde tu navegador.

---

## ⚖️ Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.