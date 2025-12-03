# 📚 Documentación Interna de la Plataforma

Bienvenido a la documentación técnica de Feature Models Platform.

## 🎯 Documentación Principal

### 📦 Órdenes y Flujos

- **[Flujo de Órdenes](order-flow.md)** - Ciclo completo de una orden desde creación hasta entrega
- **[Actualización de Estado de Órdenes](order-status-update.md)** - Transiciones de estado y validaciones
- **[Referencia Rápida de Estados](order-status-quick-reference.md)** - Guía rápida de estados de orden
- **[Asignación y Entrega](order-assignment-&-delivery-lifecycle.md)** - Gestión de asignaciones a trabajadores

### 🍕 Productos y Menú

- **[Workflows de Productos](product-workflows.md)** - Gestión completa de productos
- **[Guía de Actualización de Productos](product-update-guide.md)** - Documentación técnica del endpoint PATCH de productos
- **[Gestión Batch de Imágenes](product-images-batch-guide.md)** - Upload y delete múltiple de imágenes
- **[Addons (Complementos)](addons.md)** - Sistema de ingredientes adicionales
- **[Pizzas Mitad y Mitad](half-and-half-pizzas.md)** - Configuración de pizzas personalizadas

### 🤖 Agente de texto

- **[VAPI Integration](vapi.md)** - Integración con asistente de texto
- **[Estrategia de Resolución de Productos](vapi-product-resolution-strategy.md)** - Cómo manejar ambigüedad en nombres de productos

### 💰 Ofertas y Promociones

- **[Disponibilidad de Ofertas](offer_availability_feature.md)** - Control de disponibilidad
- **[Control de Acceso a Ofertas](offer_endpoints_access_control.md)** - Permisos y seguridad
- **[Validación de Productos en Ofertas](offer_product_uniqueness_validation.md)** - Reglas de negocio

### 👥 Usuarios y Perfiles

- **[Endpoints de Perfiles](profiles-endpoints.md)** - API de perfiles de clientes y trabajadores
- **[API Keys](api_keys.md)** - Sistema de autenticación con claves API

### 🛠️ Configuración y Utilidades

- **[Comandos](commands.md)** - Comandos útiles del proyecto
- **[Base de Datos](db.md)** - Configuración y gestión de BD
- **[Logging Guide](logging-guide.md)** - Sistema de logs y debugging
- **[Documentación](docs.md)** - Generación y gestión de docs
- **[Campo is_pickup](is_pickup_field.md)** - Funcionalidad de recoger en tienda

### 📖 Meta-Documentación

- **[Guía Rápida de Scripts](scripts-guide.md)** - ⭐ **Tabla de referencia de todos los scripts**
- **[Workflow de Despliegue](deployment-workflow.md)** - Proceso completo de despliegue
- **[Flujo de Trabajo de Documentación](documentation-workflow.md)** - Cómo mantener esta documentación actualizada
- **[Seguridad de Documentación Interna](internal-docs-security.md)** - Acceso y autenticación
- **[Despliegue de Docs en Producción](production-docs-deployment.md)** - Configuración de producción

## 🔧 Herramientas y Scripts

### Scripts de Validación

**`scripts/validate_docs_config.sh`** - Validar configuración de documentación antes de desplegar

```bash
# Ejecutar antes de desplegar a producción
bash scripts/validate_docs_config.sh
```

Este script verifica:

- ✅ Carpetas de documentación existen
- ✅ Dockerfile tiene las copias correctas
- ✅ Docker Compose tiene volúmenes montados
- ✅ Scripts de build están configurados
- ✅ Middleware de protección está implementado
- ✅ Rol DEVELOPER está configurado

**Cuándo ejecutar:**

- Antes de hacer commit de cambios en docs/
- Antes de desplegar a producción
- Después de actualizar configuración de Docker

## 🚀 Inicio Rápido

### Para Desarrolladores Backend

1. Revisa el [Flujo de Órdenes](order-flow.md) para entender el proceso principal
2. Consulta [Workflows de Productos](product-workflows.md) para gestión de menú
3. Lee la [Logging Guide](logging-guide.md) para debugging

### Para Desarrolladores Frontend

1. Revisa los [Endpoints de Perfiles](profiles-endpoints.md) para la API de usuarios
2. Consulta [API Keys](api_keys.md) para autenticación
3. Lee [Actualización de Estado de Órdenes](order-status-update.md) para el tracking

### Para DevOps

1. Revisa [Comandos](commands.md) para operaciones comunes
2. Consulta [Base de Datos](db.md) para configuración
3. Lee [Flujo de Trabajo de Documentación](documentation-workflow.md) para CI/CD

## 🔍 Búsqueda

Usa la barra de búsqueda en la parte superior para encontrar información específica en toda la documentación.

## 📝 Contribuir

Para actualizar esta documentación:

1. Edita archivos en la carpeta `docs/`
2. Ejecuta: `bash scripts/build_docs.sh`
3. Verifica los cambios en `http://localhost:8000/internal-docs/`

Consulta la [guía completa de documentación](documentation-workflow.md) para más detalles.

---

**Última actualización:** {{ git.date }}
