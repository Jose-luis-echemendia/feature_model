# 🚀 Guía Rápida de Desarrollo - Feature Models

Esta guía está diseñada para desarrolladores frontend que necesitan trabajar con el backend de manera local sin configuración manual.

## 📋 Pre-requisitos

- Docker instalado y en ejecución
- Docker Compose instalado (viene con Docker Desktop)
- Git configurado
- Puerto 3000 (frontend) y 8000 (backend) disponibles

## ⚡ Inicio Rápido (Un Solo Comando)

```bash
# 1. Clonar el repositorio (si aún no lo has hecho)
git clone <url-del-repo>
cd feature_model

# 2. Copiar el archivo de variables de entorno
cp .env.example .env

# 3. ¡Levantar todo el entorno!
docker-compose -f docker-compose.dev.yml up
```

**¡Eso es todo!** El sistema automáticamente:

✅ Creará la base de datos PostgreSQL  
✅ Ejecutará todas las migraciones  
✅ Poblará la base de datos con datos de prueba  
✅ Iniciará el backend en modo desarrollo  
✅ Iniciará el frontend con hot-reload  
✅ Configurará Redis y MinIO

## 🌐 URLs de Acceso

Una vez que todo esté corriendo:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **MinIO Console**: http://localhost:9001

## 👤 Credenciales de Prueba

El sistema crea automáticamente usuarios de prueba con diferentes roles:

### Administrador

- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Permisos**: Acceso completo al sistema

### Diseñador de Modelos

- **Email**: `designer@example.com`
- **Password**: `designer123`
- **Permisos**: Crear y editar modelos de características

### Editor de Modelos

- **Email**: `editor@example.com`
- **Password**: `editor123`
- **Permisos**: Editar modelos existentes

### Configurador

- **Email**: `configurator@example.com`
- **Password**: `config123`
- **Permisos**: Crear configuraciones basadas en modelos

### Visualizador

- **Email**: `viewer@example.com`
- **Password**: `viewer123`
- **Permisos**: Solo lectura

## 📊 Datos de Prueba Incluidos

El sistema viene pre-poblado con:

- **Usuarios**: 5 usuarios con diferentes roles
- **Dominios**: E-Commerce, Healthcare, Education, IoT
- **Tags**: performance, security, ui, api, mobile, analytics, payment, authentication
- **Recursos Educativos**: Videos, PDFs, Quizzes de ejemplo
- **Modelo de Ejemplo**: "E-Commerce Platform" con características jerárquicas:
  - Product Catalog (Mandatory)
  - Shopping Cart (Mandatory)
  - Payment Processing (Mandatory)
  - User Management (Mandatory)
  - Wishlist (Optional)
  - Product Reviews (Optional)
  - Recommendations (Optional)

## 🔄 Comandos Útiles

### Ver logs en tiempo real

```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose.dev.yml logs -f

# Ver logs solo del backend
docker-compose -f docker-compose.dev.yml logs -f backend

# Ver logs solo del frontend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker-compose -f docker-compose.dev.yml restart

# Reiniciar solo el backend
docker-compose -f docker-compose.dev.yml restart backend

# Reiniciar solo el frontend
docker-compose -f docker-compose.dev.yml restart frontend
```

### Detener el entorno

```bash
# Detener sin eliminar datos
docker-compose -f docker-compose.dev.yml stop

# Detener y eliminar contenedores (mantiene volúmenes/datos)
docker-compose -f docker-compose.dev.yml down

# Detener y eliminar TODO (incluye base de datos)
docker-compose -f docker-compose.dev.yml down -v
```

### Resetear la base de datos

```bash
# 1. Detener y eliminar todo
docker-compose -f docker-compose.dev.yml down -v

# 2. Volver a iniciar (recreará todo desde cero)
docker-compose -f docker-compose.dev.yml up
```

### Ejecutar comandos en el backend

```bash
# Abrir shell en el contenedor del backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Ejecutar migraciones manualmente
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Re-ejecutar seeding (es idempotente, no duplica datos)
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data

# Crear un nuevo usuario manualmente
docker-compose -f docker-compose.dev.yml exec backend python -c "from app.crud import create_user; ..."
```

### Modo segundo plano

```bash
# Iniciar en modo detached (background)
docker-compose -f docker-compose.dev.yml up -d

# Ver estado de servicios
docker-compose -f docker-compose.dev.yml ps
```

## 🧪 Testing de la API

### Usando Swagger UI

1. Abre http://localhost:8000/docs
2. Click en "Authorize"
3. Usa credenciales de prueba (ej: `admin@example.com` / `admin123`)
4. Prueba los endpoints directamente desde el navegador

### Usando curl

```bash
# 1. Obtener token
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"

# 2. Usar el token en requests
curl -X GET "http://localhost:8000/api/v1/feature-models/" \
  -H "Authorization: Bearer <tu-token-aqui>"
```

## 📝 Desarrollo Frontend

### Hot Reload

El frontend está configurado con hot-reload automático:

- Edita archivos en `frontend/src/`
- Los cambios se reflejan automáticamente en el navegador
- No necesitas reiniciar el contenedor

### Variables de entorno frontend

Edita `frontend/.env.local` si necesitas cambiar configuraciones:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Instalar nuevas dependencias

```bash
# Opción 1: Desde fuera del contenedor
docker-compose -f docker-compose.dev.yml exec frontend npm install <paquete>

# Opción 2: Reconstruir imagen
docker-compose -f docker-compose.dev.yml up --build frontend
```

## 🔍 Troubleshooting

### Error: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto 8000
sudo lsof -i :8000

# Ver qué proceso usa el puerto 3000
sudo lsof -i :3000

# Matar el proceso o cambiar puertos en docker-compose.dev.yml
```

### Error: Base de datos no responde

```bash
# Verificar estado de servicios
docker-compose -f docker-compose.dev.yml ps

# Ver logs de la base de datos
docker-compose -f docker-compose.dev.yml logs db

# Reiniciar servicio de base de datos
docker-compose -f docker-compose.dev.yml restart db
```

### Error: Permisos en volúmenes

```bash
# En Linux, si tienes problemas de permisos
sudo chown -R $USER:$USER backend/app

# O ejecutar con tu usuario
docker-compose -f docker-compose.dev.yml up --force-recreate
```

### Backend no refleja cambios en el código

```bash
# El backend usa volúmenes, pero si no detecta cambios:
docker-compose -f docker-compose.dev.yml restart backend

# O fuerza rebuild
docker-compose -f docker-compose.dev.yml up --build backend
```

### Datos de prueba no aparecen

```bash
# Verificar que ENVIRONMENT está en "local" o "development"
docker-compose -f docker-compose.dev.yml exec backend env | grep ENVIRONMENT

# Re-ejecutar seeding manualmente
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data
```

### Limpiar todo y empezar de cero

```bash
# 1. Detener todo
docker-compose -f docker-compose.dev.yml down -v

# 2. Limpiar imágenes (opcional)
docker-compose -f docker-compose.dev.yml down --rmi all

# 3. Rebuild completo
docker-compose -f docker-compose.dev.yml build --no-cache

# 4. Iniciar de nuevo
docker-compose -f docker-compose.dev.yml up
```

## 🏗️ Arquitectura del Entorno de Desarrollo

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Frontend   │◄────►│   Backend    │                │
│  │  Next.js:3000│      │ FastAPI:8000 │                │
│  └──────────────┘      └───────┬──────┘                │
│                                 │                        │
│                        ┌────────┴────────┐              │
│                        │                 │              │
│                   ┌────▼─────┐    ┌─────▼─────┐       │
│                   │PostgreSQL│    │   Redis   │       │
│                   │  :5432   │    │   :6379   │       │
│                   └──────────┘    └───────────┘       │
│                                                          │
│                   ┌──────────────┐                      │
│                   │    MinIO     │                      │
│                   │ :9000, :9001 │                      │
│                   └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## 📚 Siguiente Pasos

1. **Explora la API**: http://localhost:8000/docs
2. **Revisa el código del frontend**: `frontend/src/app/`
3. **Estudia los modelos**: `backend/app/models/`
4. **Personaliza los datos**: Edita `backend/app/seed_data.py`
5. **Lee la documentación completa**: `docs/README.md`

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs: `docker-compose -f docker-compose.dev.yml logs`
2. Verifica el estado: `docker-compose -f docker-compose.dev.yml ps`
3. Consulta esta guía de troubleshooting
4. Contacta al equipo de backend

---

**¡Happy Coding! 🚀**
