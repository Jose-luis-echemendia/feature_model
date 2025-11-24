# ✅ CHECKLIST DE DESPLIEGUE EN PRODUCCIÓN

## 📋 Pre-despliegue

### Configuración de Archivos

- [x] **Dockerfile del frontend** creado y optimizado
- [x] **next.config.ts** configurado con `output: 'standalone'`
- [x] **nginx.conf** actualizado para proxy a Next.js
- [x] **docker-compose.prod.yml** corregido (sintaxis y puertos)
- [x] **.dockerignore** optimizado para reducir tamaño de build

### Validación

- [x] Ejecutar `./validate_deployment.sh` - Sin errores
- [ ] Variables de entorno configuradas en `.env`
- [ ] Redes de Docker creadas (`traefik-public`, `internal_network`)
- [ ] Volúmenes externos creados (`featuremodels-db-data`)

## 🔧 Variables de Entorno Requeridas

Verifica que tu archivo `.env` contenga:

```bash
# Dominio y URLs
DOMAIN=tu-dominio.com
FRONTEND_HOST=https://dashboard.tu-dominio.com
STACK_NAME=feature-models

# Imágenes Docker
DOCKER_IMAGE_FRONTEND=tu-registry/feature-models-frontend
DOCKER_IMAGE_BACKEND=tu-registry/feature-models-backend
TAG=latest

# PostgreSQL
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis123
POSTGRES_DB=feature_models

# Seguridad
SECRET_KEY=tu-secret-key-muy-segura-y-larga-aqui
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis123

# Email (opcional)
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@tu-dominio.com

# CORS
BACKEND_CORS_ORIGINS=["https://dashboard.tu-dominio.com"]

# Ambiente
ENVIRONMENT=production

# Sentry (opcional)
SENTRY_DSN=
```

## 🌐 Configuración de Red

### 1. Crear redes de Docker

```bash
# Red pública (para Traefik)
docker network create traefik-public

# Red interna (para comunicación entre servicios)
docker network create internal_network
```

### 2. Crear volúmenes

```bash
# Volumen para PostgreSQL
docker volume create featuremodels-db-data
```

## 🚀 Proceso de Despliegue

### Opción 1: Despliegue Manual

```bash
# 1. Validar configuración
./validate_deployment.sh

# 2. Construir imágenes
docker build -t ${DOCKER_IMAGE_BACKEND}:${TAG} ./backend

docker build -t ${DOCKER_IMAGE_FRONTEND}:${TAG} \
  --build-arg VITE_API_URL=https://api.${DOMAIN} \
  --build-arg NODE_ENV=production \
  ./frontend

# 3. Push a registry (si es necesario)
docker push ${DOCKER_IMAGE_BACKEND}:${TAG}
docker push ${DOCKER_IMAGE_FRONTEND}:${TAG}

# 4. Desplegar servicios
docker-compose -f docker-compose.prod.yml up -d

# 5. Verificar estado
docker-compose -f docker-compose.prod.yml ps

# 6. Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Opción 2: Usando el Script Interactivo

```bash
./deploy.sh
# Seguir las opciones del menú
```

## 🔍 Verificación Post-Despliegue

### 1. Verificar que todos los servicios estén corriendo

```bash
docker-compose -f docker-compose.prod.yml ps
```

Deberías ver:

- ✅ `db` - healthy
- ✅ `prestart` - exited (0)
- ✅ `redis` - running
- ✅ `feature_models_backend` - healthy
- ✅ `celery_worker` - running
- ✅ `frontend` - running

### 2. Verificar logs

```bash
# Logs del backend
docker-compose -f docker-compose.prod.yml logs -f feature_models_backend

# Logs del frontend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 3. Probar endpoints

```bash
# Health check del backend
curl https://api.${DOMAIN}/api/v1/utils/health-check/

# Frontend
curl https://dashboard.${DOMAIN}
```

### 4. Verificar base de datos

```bash
# Conectar a PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Verificar tablas
\dt

# Verificar usuarios
SELECT email FROM users;
```

## 🔒 Seguridad Post-Despliegue

- [ ] Cambiar `POSTGRES_PASSWORD` por una contraseña fuerte
- [ ] Cambiar `SECRET_KEY` por una clave aleatoria de al menos 32 caracteres
- [ ] Cambiar `FIRST_SUPERUSER_PASSWORD`
- [ ] Configurar firewall para permitir solo puertos 80 y 443
- [ ] Verificar que Traefik esté generando certificados SSL
- [ ] Revisar políticas de CORS en `BACKEND_CORS_ORIGINS`
- [ ] Configurar backups automáticos de la base de datos

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Detener servicios
docker-compose -f docker-compose.prod.yml down

# Reiniciar un servicio específico
docker-compose -f docker-compose.prod.yml restart frontend

# Reconstruir y redesplegar
docker-compose -f docker-compose.prod.yml up -d --build

# Ver recursos utilizados
docker stats
```

### Base de Datos

```bash
# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec feature_models_backend alembic upgrade head

# Crear backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
  -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose -f docker-compose.prod.yml exec -T db psql \
  -U ${POSTGRES_USER} ${POSTGRES_DB} < backup_20241123.sql
```

### Logs y Debugging

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs -f frontend

# Ver últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs --tail=100

# Entrar a un contenedor
docker-compose -f docker-compose.prod.yml exec frontend sh
docker-compose -f docker-compose.prod.yml exec feature_models_backend bash
```

## 📊 Monitoreo

### Métricas a Vigilar

1. **CPU y Memoria**

   ```bash
   docker stats
   ```

2. **Espacio en Disco**

   ```bash
   df -h
   docker system df
   ```

3. **Logs de Errores**

   ```bash
   docker-compose -f docker-compose.prod.yml logs --tail=50 | grep -i error
   ```

4. **Healthchecks**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

## 🔄 Actualización de Servicios

### Actualizar Backend

```bash
# 1. Construir nueva imagen
docker build -t ${DOCKER_IMAGE_BACKEND}:${TAG} ./backend

# 2. Detener servicio
docker-compose -f docker-compose.prod.yml stop feature_models_backend

# 3. Ejecutar migraciones (si hay)
docker-compose -f docker-compose.prod.yml run --rm prestart

# 4. Iniciar servicio actualizado
docker-compose -f docker-compose.prod.yml up -d feature_models_backend
```

### Actualizar Frontend

```bash
# 1. Construir nueva imagen
docker build -t ${DOCKER_IMAGE_FRONTEND}:${TAG} \
  --build-arg VITE_API_URL=https://api.${DOMAIN} \
  --build-arg NODE_ENV=production \
  ./frontend

# 2. Redesplegar
docker-compose -f docker-compose.prod.yml up -d frontend
```

## 🚨 Troubleshooting

### El Frontend no responde

1. Verificar logs: `docker-compose -f docker-compose.prod.yml logs frontend`
2. Verificar que Next.js esté corriendo en puerto 3000
3. Verificar configuración de Traefik
4. Verificar variables de entorno `VITE_API_URL`

### El Backend retorna 502

1. Verificar healthcheck: `docker-compose -f docker-compose.prod.yml ps`
2. Verificar logs: `docker-compose -f docker-compose.prod.yml logs feature_models_backend`
3. Verificar conexión a PostgreSQL
4. Verificar puerto 8000

### Base de datos no conecta

1. Verificar que el contenedor de PostgreSQL esté corriendo
2. Verificar variables de entorno (`POSTGRES_*`)
3. Verificar volumen de datos
4. Revisar logs: `docker-compose -f docker-compose.prod.yml logs db`

### Celery worker no procesa tareas

1. Verificar conexión a Redis
2. Verificar logs: `docker-compose -f docker-compose.prod.yml logs celery_worker`
3. Verificar configuración de Celery en el código

## 📝 Notas Adicionales

- **Traefik** debe estar corriendo y configurado previamente
- Los certificados SSL se generan automáticamente vía Let's Encrypt
- Los logs se mantienen en los contenedores, considera usar un sistema de logging centralizado
- Implementa backups regulares de la base de datos
- Monitorea el uso de recursos del servidor

---

**¿Necesitas ayuda?** Consulta el archivo `DEPLOYMENT_FIXES.md` para más detalles sobre la arquitectura y configuración.
