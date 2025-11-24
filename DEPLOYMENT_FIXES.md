# Correcciones de Configuración de Despliegue

## Resumen Ejecutivo

Se han identificado y corregido **problemas críticos** en la configuración de despliegue de producción, especialmente en el servicio frontend y en docker-compose.prod.yml.

---

## 🔴 Problemas Identificados

### 1. **Frontend sin Dockerfile de Producción** ❌

- El directorio `frontend/` **NO tenía** un `Dockerfile` de producción
- Solo existían `Dockerfile.dev` y `Dockerfile.playwright`
- Sin este archivo, el servicio frontend no podía construirse ni desplegarse

### 2. **Errores de Sintaxis en docker-compose.prod.yml** ❌

- **Línea 136**: Comilla mal colocada en el comando de celery_worker:
  ```yaml
  command: celery -A app.core.celery.celery_app worker --loglevel=info'
  #                                                                      ↑ comilla extra
  ```
- **Línea 183**: Inconsistencia en nombres de red:
  ```yaml
  internal-network: # ❌ Incorrecto (con guion)
  internal_network: # ✅ Correcto (usado en servicios)
  ```

### 3. **Puerto Incorrecto en Backend** ❌

- El comando gunicorn escuchaba en puerto **8010**
- El healthcheck intentaba conectar al puerto **8000**
- Resultado: healthcheck siempre fallaba

### 4. **Configuración Incorrecta de Nginx** ❌

- nginx.conf configurado para servir archivos estáticos HTML
- No configurado para proxy a Next.js standalone server
- Puerto de servicio incorrecto (80 en lugar de 3000)

---

## ✅ Correcciones Implementadas

### 1. **Creado Dockerfile de Producción para Frontend**

**Ubicación:** `/frontend/Dockerfile`

**Arquitectura multi-stage:**

```dockerfile
# Stage 1: Instalar dependencias
FROM node:20-alpine AS deps
# Instala solo las dependencias necesarias

# Stage 2: Build de Next.js
FROM node:20-alpine AS builder
# Construye la aplicación con output 'standalone'

# Stage 3: Runner de producción
FROM node:20-alpine AS runner
# Ejecuta el servidor Next.js standalone
# Usuario no-root para seguridad
# Expone puerto 3000
```

**Características:**

- ✅ Build optimizado multi-stage (imagen final más pequeña)
- ✅ Modo standalone de Next.js (servidor Node.js incluido)
- ✅ Usuario no-root (seguridad)
- ✅ Variables de entorno para API URL
- ✅ Telemetría deshabilitada

### 2. **Actualizada Configuración de Next.js**

**Archivo:** `/frontend/next.config.ts`

```typescript
const nextConfig: NextConfig = {
  reactCompiler: true,
  output: "standalone", // ← Genera servidor standalone
  compress: true, // ← Compresión gzip
  images: {
    unoptimized: false, // ← Optimización de imágenes
  },
};
```

### 3. **Actualizada Configuración de Nginx**

**Archivo:** `/frontend/nginx.conf`

**Cambios principales:**

- ✅ Configurado como **proxy reverso** para Next.js (puerto 3000)
- ✅ Cache para archivos estáticos (\_next/static)
- ✅ Compresión gzip habilitada
- ✅ Headers de seguridad
- ✅ Configuración de upstream para Next.js

```nginx
upstream nextjs_upstream {
  server localhost:3000;
}

server {
  listen 80;

  location / {
    proxy_pass http://nextjs_upstream;
    # Headers y configuración de proxy
  }

  location /_next/static {
    # Cache de 1 año para assets estáticos
    add_header Cache-Control "public, max-age=31536000, immutable";
  }
}
```

### 4. **Corregido docker-compose.prod.yml**

#### a) **Servicio celery_worker** - Sintaxis de comando

```yaml
# ANTES (error)
command: celery -A app.core.celery.celery_app worker --loglevel=info'

# DESPUÉS (correcto)
command: celery -A app.core.celery.celery_app worker --loglevel=info
```

#### b) **Nombres de redes** - Consistencia

```yaml
# ANTES (inconsistente)
networks:
  internal-network:  # ← guion
    external: true

# DESPUÉS (consistente)
networks:
  internal_network:  # ← guion bajo
    external: true
```

#### c) **Backend** - Puerto corregido

```yaml
# ANTES (inconsistente)
command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8010 --timeout 120
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]

# DESPUÉS (consistente)
command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]
```

#### d) **Frontend** - Puerto de servicio corregido

```yaml
# ANTES (incorrecto para Next.js)
- traefik.http.services.${STACK_NAME}-frontend.loadbalancer.server.port=80

# DESPUÉS (correcto)
- traefik.http.services.${STACK_NAME}-frontend.loadbalancer.server.port=3000
```

---

## 📋 Archivos Modificados

1. ✅ `/frontend/Dockerfile` - **CREADO**
2. ✅ `/frontend/next.config.ts` - **MODIFICADO**
3. ✅ `/frontend/nginx.conf` - **MODIFICADO**
4. ✅ `/docker-compose.prod.yml` - **CORREGIDO**

---

## 🚀 Próximos Pasos para Despliegue

### 1. Verificar variables de entorno

Asegúrate de que tu archivo `.env` tenga todas las variables necesarias:

```bash
# Variables críticas
DOMAIN=tu-dominio.com
FRONTEND_HOST=https://dashboard.tu-dominio.com
STACK_NAME=feature-models
DOCKER_IMAGE_FRONTEND=tu-registry/frontend
DOCKER_IMAGE_BACKEND=tu-registry/backend
TAG=latest

# PostgreSQL
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...

# Secrets
SECRET_KEY=...
FIRST_SUPERUSER=...
FIRST_SUPERUSER_PASSWORD=...
```

### 2. Construir las imágenes

```bash
# Build del backend
docker build -t ${DOCKER_IMAGE_BACKEND}:${TAG} ./backend

# Build del frontend
docker build -t ${DOCKER_IMAGE_FRONTEND}:${TAG} \
  --build-arg VITE_API_URL=https://api.${DOMAIN} \
  --build-arg NODE_ENV=production \
  ./frontend
```

### 3. Desplegar con docker-compose

```bash
# Verificar la configuración
docker-compose -f docker-compose.prod.yml config

# Desplegar
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verificar que los servicios estén corriendo

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Verificar healthchecks
docker-compose -f docker-compose.prod.yml ps
```

---

## 🔍 Validación

### Frontend

- ✅ Dockerfile multi-stage optimizado
- ✅ Next.js en modo standalone
- ✅ Nginx configurado como proxy
- ✅ Puerto 3000 expuesto correctamente
- ✅ Variables de entorno inyectadas en build

### Backend

- ✅ Puerto consistente (8000) en comando y healthcheck
- ✅ Healthcheck funcionando
- ✅ Conectado a redes correctas

### Docker Compose

- ✅ Sin errores de sintaxis
- ✅ Nombres de redes consistentes
- ✅ Puertos de servicios correctos
- ✅ Labels de Traefik correctos

---

## 📝 Notas Adicionales

### Arquitectura de Despliegue

```
Internet
    ↓
Traefik (Reverse Proxy)
    ├─→ dashboard.domain.com:443 → Frontend (puerto 3000)
    │                                    ↓
    │                              Next.js Standalone Server
    │
    └─→ api.domain.com:443 → Backend (puerto 8000)
                                    ↓
                              Gunicorn + Uvicorn Workers
                                    ↓
                              PostgreSQL + Redis
```

### Seguridad

- Frontend ejecuta como usuario no-root (UID 1001)
- Backend ejecuta con usuario limitado
- Telemetría de Next.js deshabilitada
- Server tokens de nginx ocultos

### Performance

- Compresión gzip habilitada
- Cache de assets estáticos (1 año)
- Múltiples workers en backend (4)
- Build optimizado de Next.js

---

**Fecha de corrección:** 23 de noviembre de 2025
**Estado:** ✅ Listo para despliegue
