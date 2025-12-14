# 📚 Documentación Backend - Feature Model System

Documentación técnica del backend del sistema de Feature Models para gestión de líneas de productos software (SPL).

## 📋 Tabla de Contenidos

### 🏗️ Arquitectura y Diseño

- **[db.md](./backend_db.md)** - Documentación de la base de datos y esquema
- **[s3_architecture.md](./backend_s3_architecture.md)** - Arquitectura del servicio S3 para almacenamiento
- **[s3_service_changes.md](./backend_s3_service_changes.md)** - Cambios en el servicio S3
- **[s3_service_usage.md](./backend_s3_service_usage.md)** - Guía de uso del servicio S3
- **[s3_dependency_examples.md](./backend_s3_dependency_examples.md)** - Ejemplos de inyección de dependencias S3

### 🔌 APIs y Endpoints

- **[tree.md](./tree.md)** - 📋 **Estructura de respuesta del endpoint `/complete/`** - Documentación detallada de cada campo del JSON de respuesta
- **[COMPLETE_STRUCTURE_API.md](./COMPLETE_STRUCTURE_API.md)** - API para obtener estructura completa del Feature Model
- **[STATISTICS_API.md](./STATISTICS_API.md)** - API de estadísticas (REST + WebSocket)
- **[REST_VS_WEBSOCKET.md](./REST_VS_WEBSOCKET.md)** - Comparación y casos de uso REST vs WebSocket
- **[FEATURE_MODEL_VERSIONS_INFO.md](./FEATURE_MODEL_VERSIONS_INFO.md)** - Información sobre versionado de Feature Models
- **[user_endpoints_migration.md](./user_endpoints_migration.md)** - Migración de endpoints de usuarios
- **[EXCEPTIONS_DOCUMENTATION.md](./EXCEPTIONS_DOCUMENTATION.md)** - ⚠️ **Excepciones personalizadas de Feature Models** - Códigos HTTP, mensajes y casos de uso
- **[DOMAIN_EXCEPTIONS_DOCUMENTATION.md](./DOMAIN_EXCEPTIONS_DOCUMENTATION.md)** - ⚠️ **Excepciones personalizadas de Dominios** - Sistema completo de excepciones para operaciones de dominio

### 🔐 Autenticación y Seguridad

- **[LOGIN_REFACTOR_SUMMARY.md](./backend_LOGIN_REFACTOR_SUMMARY.md)** - Resumen de refactorización del sistema de login
- **[LOGIN_ENDPOINTS_REFACTOR.md](./backend_LOGIN_ENDPOINTS_REFACTOR.md)** - Detalles de refactorización de endpoints de login
- **[user_role.md](./backend_user_role.md)** - Sistema de roles y permisos

### 🐛 Resolución de Problemas y Bugs

- **[ROUTE_ORDER_FIX.md](./backend_ROUTE_ORDER_FIX.md)** - Solución a errores 422 por orden de rutas en FastAPI
- **[MIGRATION_ORDER_FIX.md](./backend_MIGRATION_ORDER_FIX.md)** - Corrección de orden en migraciones de base de datos
- **[ENUM_COMPARISON_BEST_PRACTICES.md](./backend_ENUM_COMPARISON_BEST_PRACTICES.md)** - Mejores prácticas para comparación de enums

### 🚀 Servicios y Utilidades

- **[PRESTART_SERVICE.md](./backend_PRESTART_SERVICE.md)** - Servicio de inicialización pre-arranque
- **[README_S3_REFACTORING.md](./backend_README_S3_REFACTORING.md)** - Refactorización del servicio S3
- **[commands.md](./backend_commands.md)** - Comandos útiles del proyecto
- **[DEPENDENCIES_SUMMARY.md](./DEPENDENCIES_SUMMARY.md)** - 📦 **Resumen de dependencias de servicios** - Estado de SymPy y NetworkX
- **[DEPENDENCIES_SERVICES.md](./DEPENDENCIES_SERVICES.md)** - 📦 **Dependencias detalladas** - Guía completa de instalación y configuración

### 📝 Implementación y Sumarios

- **[IMPLEMENTATION_SUMMARY.md](./backend_IMPLEMENTATION_SUMMARY.md)** - Resumen de implementaciones importantes
- **[EXCEPTIONS_IMPLEMENTATION_SUMMARY.md](./EXCEPTIONS_IMPLEMENTATION_SUMMARY.md)** - ⚠️ **Implementación de excepciones FM** - Resumen ejecutivo del sistema de excepciones
- **[DOMAIN_EXCEPTIONS_IMPLEMENTATION_SUMMARY.md](./DOMAIN_EXCEPTIONS_IMPLEMENTATION_SUMMARY.md)** - ⚠️ **Implementación de excepciones de Dominios** - Estadísticas y archivos modificados
- **[suggestions_code.md](./backend_suggestions_code.md)** - Sugerencias y mejoras de código
- **[rf.md](./backend_rf.md)** - Requisitos funcionales

### 🎓 Casos de Uso Educativos

- **[CAMBIOS_EDUCATIVOS.md](./backend_CAMBIOS_EDUCATIVOS.md)** - Cambios en el contexto educativo
- **[MAESTRIA_CIENCIA_DATOS.md](./backend_MAESTRIA_CIENCIA_DATOS.md)** - Caso de uso: Maestría en Ciencia de Datos

---

## 🎯 Documentos Destacados

### Para Desarrolladores Frontend

1. **[tree.md](./backend_tree.md)** - **⭐ ESENCIAL:** Entender la estructura completa del JSON que devuelve `/complete/`
2. **[STATISTICS_API.md](./backend_STATISTICS_API.md)** - Cómo consumir estadísticas en tiempo real
3. **[REST_VS_WEBSOCKET.md](./backend_REST_VS_WEBSOCKET.md)** - Cuándo usar cada tecnología

### Para Nuevos Desarrolladores Backend

1. **[db.md](./backend_db.md)** - Comprender el esquema de base de datos
2. **[EXCEPTIONS_DOCUMENTATION.md](./EXCEPTIONS_DOCUMENTATION.md)** - ⭐ Sistema completo de excepciones
3. **[DEPENDENCIES_SUMMARY.md](./DEPENDENCIES_SUMMARY.md)** - ⭐ Dependencias necesarias (SymPy, NetworkX)
4. **[ENUM_COMPARISON_BEST_PRACTICES.md](./backend_ENUM_COMPARISON_BEST_PRACTICES.md)** - Evitar errores comunes
5. **[ROUTE_ORDER_FIX.md](./backend_ROUTE_ORDER_FIX.md)** - Evitar errores 422 en rutas
6. **[commands.md](./backend_commands.md)** - Comandos esenciales

### Para Arquitectos y Tech Leads

1. **[s3_architecture.md](./backend_s3_architecture.md)** - Arquitectura de almacenamiento
2. **[LOGIN_REFACTOR_SUMMARY.md](./backend_LOGIN_REFACTOR_SUMMARY.md)** - Evolución del sistema de autenticación
3. **[IMPLEMENTATION_SUMMARY.md](./backend_IMPLEMENTATION_SUMMARY.md)** - Decisiones técnicas importantes

---

## 📊 Estructura de Carpetas

```
docs/
├── README.md (este archivo - índice principal)
├── tree.md ⭐ (Estructura JSON del endpoint /complete/)
├── STATISTICS_API.md (APIs de estadísticas)
├── db.md (Base de datos)
├── s3_*.md (Servicios S3)
├── LOGIN_*.md (Sistema de autenticación)
├── *_FIX.md (Soluciones a problemas comunes)
└── assets/ (Recursos: imágenes, diagramas)
```

---

## 🔍 Búsqueda Rápida

¿Buscando algo específico?

- **Errores 422 en rutas:** [ROUTE_ORDER_FIX.md](./backend_ROUTE_ORDER_FIX.md)
- **Comparación de enums:** [ENUM_COMPARISON_BEST_PRACTICES.md](./backend_ENUM_COMPARISON_BEST_PRACTICES.md)
- **Respuesta del endpoint /complete/:** [tree.md](./backend_tree.md)
- **WebSockets:** [REST_VS_WEBSOCKET.md](./backend_REST_VS_WEBSOCKET.md)
- **Migraciones de BD:** [MIGRATION_ORDER_FIX.md](./backend_MIGRATION_ORDER_FIX.md)
- **Almacenamiento S3:** [s3_architecture.md](./backend_s3_architecture.md)

---

## 📝 Contribuir a la Documentación

Al agregar nueva documentación:

1. Crear archivo con nombre descriptivo en `PascalCase` o `snake_case`
2. Agregar entrada en este README en la sección apropiada
3. Incluir ejemplos de código cuando sea posible
4. Marcar con ⭐ si es documentación esencial

---

**Última actualización:** Diciembre 2025
