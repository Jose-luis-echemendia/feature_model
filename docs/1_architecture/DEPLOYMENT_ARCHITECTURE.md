# 🏗️ Arquitectura de Despliegue en Producción

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                          INTERNET                                │
│                             ↓                                    │
│                    (HTTPS - Puerto 443)                          │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                    TRAEFIK (Reverse Proxy)                      │
│  • Enrutamiento basado en Host                                 │
│  • Certificados SSL automáticos (Let's Encrypt)                │
│  • Red: traefik-public                                         │
└──────────────┬─────────────────────────┬───────────────────────┘
               ↓                         ↓
    ┌──────────────────┐      ┌──────────────────┐
    │ dashboard.domain │      │  api.domain      │
    │   (Frontend)     │      │  (Backend)       │
    └────────┬─────────┘      └────────┬─────────┘
             ↓                         ↓
┌────────────────────────┐  ┌─────────────────────────┐
│   FRONTEND SERVICE     │  │   BACKEND SERVICE       │
│ ┌────────────────────┐ │  │ ┌─────────────────────┐ │
│ │   Next.js          │ │  │ │  Gunicorn           │ │
│ │   Standalone       │ │  │ │  + Uvicorn Workers  │ │
│ │   Server           │ │  │ │  (4 workers)        │ │
│ │   Puerto: 3000     │ │  │ │  Puerto: 8000       │ │
│ └────────────────────┘ │  │ └─────────────────────┘ │
│                        │  │                         │
│ • Node 20 Alpine       │  │ • Python 3.10+          │
│ • Usuario no-root      │  │ • FastAPI + SQLModel    │
│ • Build optimizado     │  │ • Healthcheck activo    │
│ • Red: public +        │  │ • Red: public +         │
│   internal_network     │  │   internal_network      │
└────────────────────────┘  └──────────┬──────────────┘
                                       ↓
                         ┌─────────────────────────────┐
                         │    PRESTART SERVICE         │
                         │  • Migraciones Alembic      │
                         │  • Crear superusuario       │
                         │  • Inicialización DB        │
                         │  • Depende de: db (healthy) │
                         └─────────────┬───────────────┘
                                       ↓
              ┌────────────────────────┴────────────────────────┐
              ↓                                                  ↓
┌─────────────────────────┐                    ┌─────────────────────────┐
│   POSTGRESQL SERVICE    │                    │   REDIS SERVICE         │
│ ┌─────────────────────┐ │                    │ ┌─────────────────────┐ │
│ │  PostgreSQL 17      │ │                    │ │  Redis 7 Alpine     │ │
│ │  Puerto: 5432       │ │                    │ │  Puerto: 6379       │ │
│ └─────────────────────┘ │                    │ └─────────────────────┘ │
│                         │                    │                         │
│ • Volumen persistente:  │                    │ • Cache de sesiones     │
│   featuremodels-db-data │                    │ • Cola de Celery        │
│ • Healthcheck activo    │                    │ • Volumen: redis_data   │
│ • Red: internal_network │                    │ • Red: internal_network │
└─────────────────────────┘                    └───────────┬─────────────┘
                                                           ↓
                                              ┌─────────────────────────┐
                                              │  CELERY WORKER SERVICE  │
                                              │ ┌─────────────────────┐ │
                                              │ │  Celery Worker      │ │
                                              │ │  Tareas asíncronas  │ │
                                              │ └─────────────────────┘ │
                                              │                         │
                                              │ • Depende de: Redis, DB │
                                              │ • Red: internal_network │
                                              └─────────────────────────┘
```

## Flujo de Peticiones

### 1. Usuario accede al Frontend

```
Usuario → https://dashboard.domain.com
    ↓
Traefik (puerto 443, SSL/TLS)
    ↓
Frontend Service (Next.js en puerto 3000)
    ↓
Respuesta HTML + JavaScript
```

### 2. Frontend realiza peticiones a la API

```
Frontend (JavaScript) → https://api.domain.com/api/v1/...
    ↓
Traefik (puerto 443, SSL/TLS)
    ↓
Backend Service (Gunicorn en puerto 8000)
    ↓
    ├─→ PostgreSQL (consultas de datos)
    ├─→ Redis (cache, sesiones)
    └─→ Celery Worker (tareas asíncronas)
    ↓
Respuesta JSON
```

## Detalles de Servicios

### Frontend Container

```yaml
Imagen: feature-models-frontend:latest
Base: node:20-alpine
Proceso: node server.js (Next.js standalone)
Puerto Interno: 3000
Redes: public, internal_network
Variables de Entorno:
  - NEXT_PUBLIC_API_URL=https://api.domain.com
  - NODE_ENV=production
  - HOSTNAME=0.0.0.0
  - PORT=3000
```

### Backend Container

```yaml
Imagen: feature-models-backend:latest
Base: python:3.10+
Proceso: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
Puerto Interno: 8000
Redes: public, internal_network
Healthcheck: curl http://localhost:8000/api/v1/utils/health-check/
Variables de Entorno:
  - POSTGRES_SERVER=db
  - POSTGRES_PORT=5432
  - DOMAIN, SECRET_KEY, etc.
```

### PostgreSQL Container

```yaml
Imagen: postgres:17
Puerto Interno: 5432
Volumen: featuremodels-db-data:/var/lib/postgresql/data/pgdata
Red: internal_network
Healthcheck: pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
Variables de Entorno:
  - POSTGRES_USER
  - POSTGRES_PASSWORD
  - POSTGRES_DB
  - PGDATA=/var/lib/postgresql/data/pgdata
```

### Redis Container

```yaml
Imagen: redis:7-alpine
Puerto Interno: 6379
Volumen: redis_data:/data
Red: internal_network
```

### Celery Worker Container

```yaml
Imagen: feature-models-backend:latest (misma que backend)
Proceso: celery -A app.core.celery.celery_app worker --loglevel=info
Red: internal_network
Depende de: db, redis
```

## Redes Docker

### traefik-public (Externa)

- Compartida con Traefik
- Permite que Traefik enrute tráfico a los servicios
- Servicios conectados: `frontend`, `feature_models_backend`

### internal_network (Externa)

- Comunicación interna entre servicios
- NO expuesta a internet
- Servicios conectados: todos excepto cuando necesitan acceso público

## Volúmenes Persistentes

### featuremodels-db-data

- **Propósito**: Almacenar datos de PostgreSQL
- **Tipo**: External (creado manualmente)
- **Ubicación**: Gestionado por Docker
- **Backup**: Necesario configurar backups regulares

### redis_data

- **Propósito**: Persistencia de Redis (opcional pero recomendado)
- **Tipo**: Named volume
- **Ubicación**: Gestionado por Docker

## Seguridad

### Niveles de Seguridad

1. **Capa de Red**

   - Firewall del servidor: solo puertos 80, 443 abiertos
   - Redes Docker aisladas
   - Servicios internos NO expuestos directamente

2. **Capa de Aplicación**

   - CORS configurado correctamente
   - JWT para autenticación
   - HTTPS obligatorio (redireccionamiento automático)
   - Usuarios no-root en contenedores

3. **Capa de Datos**
   - PostgreSQL accesible solo desde internal_network
   - Passwords seguros en variables de entorno
   - Backups regulares

## Escalabilidad

### Backend

- Actualmente: 4 workers de Gunicorn
- Escalable horizontalmente: aumentar número de workers
- O desplegar múltiples instancias con load balancer

### Frontend

- Servidor standalone de Next.js
- Escalable horizontalmente: múltiples instancias detrás de Traefik

### Base de Datos

- Actualmente: Single instance
- Para producción alta disponibilidad: PostgreSQL con réplicas
- O usar servicio gestionado (AWS RDS, Azure Database, etc.)

### Cache

- Redis puede configurarse en cluster
- Actualmente: Single instance suficiente para cargas moderadas

## Monitoreo y Observabilidad

### Healthchecks Configurados

```yaml
Backend:
  - Endpoint: /api/v1/utils/health-check/
  - Intervalo: 10s
  - Timeout: 5s
  - Retries: 5

PostgreSQL:
  - Comando: pg_isready
  - Intervalo: 10s
  - Timeout: 10s
  - Retries: 5
```

### Logs

- **Ubicación**: STDOUT/STDERR de cada contenedor
- **Acceso**: `docker-compose logs -f [servicio]`
- **Recomendación**: Implementar solución centralizada (ELK, Loki, etc.)

### Métricas

- **Recursos**: `docker stats`
- **Aplicación**: Considerar Prometheus + Grafana
- **APM**: Sentry configurado (opcional)

## Proceso de Deployment

```
1. Desarrollador hace push a Git
2. CI/CD construye imágenes Docker
3. Push de imágenes a registry
4. Pull de imágenes en servidor de producción
5. docker-compose up -d (zero-downtime con healthchecks)
6. Traefik detecta nuevos servicios automáticamente
7. Certificados SSL generados/renovados automáticamente
```

## Consideraciones de Producción

### Crítico

- ✅ Backups automáticos de base de datos
- ✅ Monitoreo de recursos del servidor
- ✅ Alertas de errores (Sentry, etc.)
- ✅ Certificados SSL renovados automáticamente
- ✅ Logs centralizados

### Recomendado

- 🔄 Implementar CI/CD completo
- 🔄 Monitoreo de aplicación (APM)
- 🔄 Testing automático
- 🔄 Blue-green deployment
- 🔄 Disaster recovery plan

### Opcional pero Útil

- ⚙️ Auto-scaling basado en carga
- ⚙️ CDN para assets estáticos
- ⚙️ Rate limiting
- ⚙️ Web Application Firewall (WAF)

---

**Nota**: Esta arquitectura está optimizada para cargas pequeñas a medianas. Para aplicaciones de alta escala, considera usar Kubernetes, servicios gestionados en la nube, o arquitecturas de microservicios.
