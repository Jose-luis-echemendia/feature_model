


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
