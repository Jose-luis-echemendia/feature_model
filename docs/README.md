

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