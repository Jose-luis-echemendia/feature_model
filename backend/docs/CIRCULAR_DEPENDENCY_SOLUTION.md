# Solución a la Dependencia Circular: features ↔ feature_groups

## El Problema

Al ejecutar `alembic upgrade head`, se producía el siguiente error:

```
psycopg.errors.UndefinedTable: relation "feature_groups" does not exist
```

Esto ocurría porque la tabla `features` intentaba crear una **Foreign Key** hacia `feature_groups.id` (columna `group_id`), pero `feature_groups` aún no había sido creada.

### ¿Por qué existe este problema?

Hay una **dependencia circular** entre dos tablas:

1. **`features`** → necesita `group_id` que referencia a → **`feature_groups.id`**
2. **`feature_groups`** → necesita `parent_feature_id` que referencia a → **`features.id`**

Es imposible crear una tabla antes que la otra si ambas se referencian mutuamente en el momento de la creación.

## La Solución

Para resolver esta dependencia circular, usamos la técnica de **creación diferida de Foreign Keys**:

### Paso 1: Crear `features` SIN la FK a `feature_groups`

```python
op.create_table(
    "features",
    sa.Column("group_id", sa.Uuid(), nullable=True),  # Columna existe
    # ... otras columnas ...
    # ❌ NO incluimos: sa.ForeignKeyConstraint(["group_id"], ["feature_groups.id"])
)
```

### Paso 2: Crear `feature_groups` CON la FK a `features`

```python
op.create_table(
    "feature_groups",
    sa.Column("parent_feature_id", sa.Uuid(), nullable=False),
    # ... otras columnas ...
    sa.ForeignKeyConstraint(["parent_feature_id"], ["features.id"]),  # ✅ Ahora features ya existe
)
```

### Paso 3: Agregar la FK desde `features.group_id` a `feature_groups.id`

```python
# Ahora que ambas tablas existen, agregamos la FK que faltaba
op.create_foreign_key(
    "fk_features_group_id_feature_groups",  # Nombre de la constraint
    "features",                              # Tabla origen
    "feature_groups",                        # Tabla destino
    ["group_id"],                            # Columna origen
    ["id"],                                  # Columna destino
)
```

## Actualización del Downgrade

Para revertir la migración correctamente, debemos hacer lo inverso:

1. **Eliminar primero** la FK que agregamos manualmente
2. Luego eliminar `feature_groups`
3. Finalmente eliminar `features`

```python
def downgrade():
    # ...

    # NIVEL 6: feature_groups
    # Primero eliminamos la FK desde features.group_id
    op.drop_constraint(
        "fk_features_group_id_feature_groups",
        "features",
        type_="foreignkey"
    )
    op.drop_table("feature_groups")

    # NIVEL 5: features
    op.drop_table("features")
```

## Resultado

✅ **Ahora la migración se ejecuta correctamente** sin errores de tablas inexistentes.

✅ **Ambas tablas mantienen su relación bidireccional** una vez creadas.

✅ **El downgrade funciona correctamente** eliminando primero la constraint añadida.

## Comando para Probar

```bash
# Limpiar la base de datos (opcional)
alembic downgrade base

# Ejecutar la migración corregida
alembic upgrade head
```

---

**Fecha:** 23 de noviembre de 2025  
**Migración:** `d8b152111a20_initial_schema.py`
