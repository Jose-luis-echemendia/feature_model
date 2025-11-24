# Corrección del Orden de Creación de Tablas en Migración Alembic

## Problema Identificado

La migración inicial `d8b152111a20_initial_schema.py` tenía **errores graves en el orden de creación de tablas**, causando que las tablas se crearan antes de que existieran las tablas a las que hacían referencia mediante claves foráneas.

### Problemas específicos encontrados:

1. **`features`** se creaba ANTES que:

   - `feature_model_versions` (necesaria para `feature_model_version_id`)
   - `feature_groups` (necesaria para `group_id`)
   - `resources` (necesaria para `resource_id`)

2. **`feature_groups`** se creaba ANTES que `features`, pero necesitaba `parent_feature_id` de `features` (dependencia circular)

3. **`feature_tags`** se creaba ANTES que `features`

4. **`feature_model_versions`** se creaba DESPUÉS de tablas que dependían de él

## Solución Implementada

Se reorganizó el orden de creación de tablas siguiendo una jerarquía de dependencias en **9 niveles**:

### NIVEL 1: Tablas sin dependencias externas

- `app_settings`
- `users` (con auto-referencias permitidas)

### NIVEL 2: Tablas que dependen solo de users

- `domains`
- `resources`
- `tags`

### NIVEL 3: feature_model

- `feature_model` (depende de `domains` y `users`)

### NIVEL 4: Tablas que dependen de feature_model

- `feature_model_collaborators`
- `feature_model_versions`

### NIVEL 5: features

- `features` (depende de `feature_model_versions`, `resources`, con auto-referencias y referencia a `feature_groups` que se crea después)

### NIVEL 6: feature_groups

- `feature_groups` (depende de `features` y `feature_model_versions`)

### NIVEL 7: Relaciones de features

- `feature_tags`
- `feature_relations`

### NIVEL 8: Tablas que dependen de feature_model_versions

- `configurations`
- `constraints`

### NIVEL 9: Relaciones de configurations

- `configuration_features`
- `configuration_tags`

## Nota sobre Dependencias Circulares

Existe una **dependencia circular** entre `features` y `feature_groups`:

- `features` referencia `group_id` → `feature_groups.id`
- `feature_groups` referencia `parent_feature_id` → `features.id`

**Solución implementada:**

1. Se creó primero la tabla `features` **sin** la clave foránea hacia `feature_groups.id`
2. Luego se creó la tabla `feature_groups` con su FK hacia `features.id`
3. Finalmente se agregó la FK desde `features.group_id` hacia `feature_groups.id` usando `op.create_foreign_key()`

Esto rompe la dependencia circular permitiendo que ambas tablas existan antes de establecer todas las relaciones.

**En el downgrade:**

1. Primero se elimina la FK `fk_features_group_id_feature_groups` usando `op.drop_constraint()`
2. Luego se elimina la tabla `feature_groups`
3. Finalmente se elimina la tabla `features`

## Función downgrade()

También se corrigió la función `downgrade()` para eliminar las tablas en **orden inverso** al de creación, asegurando que no haya errores de referencias al revertir la migración.

## Verificación

Para verificar que la migración funciona correctamente:

```bash
# Ejecutar la migración
cd backend
alembic upgrade head

# Verificar las tablas creadas
# Conectarse a PostgreSQL y ejecutar:
# \dt

# Para revertir (testing)
alembic downgrade base
```

## Fecha de corrección

23 de noviembre de 2025
