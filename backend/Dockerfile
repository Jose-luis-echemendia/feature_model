FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app


# =================================================================================
#                  --- COPIA DE CARPETAS NECESARIOS ---
# =================================================================================

# Copy backend scripts
COPY ./scripts /app/scripts

# copy config files
COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

# copy backend sistem files
COPY ./app /app/app

# =================================================================================
#          --- COPIA DE LAS 3 CARPETAS DE DOCUMENTACIÓN ---
# =================================================================================

# Copiar documentación del ROOT (docs/ en la raíz del proyecto)
# Nota: En el contexto de build, ../docs NO funciona, por eso usamos volúmenes en docker-compose
# En producción, estas carpetas se copiarán explícitamente

# Copiar documentación del BACKEND (backend/docs/)
COPY ./docs /app/backend_docs

# Las carpetas root_docs y frontend_docs se montan via volúmenes en docker-compose
# para desarrollo, y se copian en producción mediante CI/CD

# Crear carpeta de internal_docs si no existe
RUN mkdir -p /app/internal_docs/docs

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# =================================================================================
#                       --- COMANDO A EJECUTAR ---
# =================================================================================

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
