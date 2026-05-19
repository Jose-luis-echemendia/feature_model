# Ejemplos de Integración: Invalidación de Caché

Estos son ejemplos de cómo integrar la invalidación inteligente de caché en los repositorios y servicios.

**Ubicación:** Agregar en archivos de repositorio cuando se escriben datos.

---

## 📝 Ejemplo 1: Invalidar al eliminar una Feature

**Archivo:** `backend/app/repositories/feature.py`

```python
# Método: delete_feature()

async def delete_feature(self, feature_id: uuid.UUID) -> None:
    """Eliminar una feature e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    # 1. Obtener la feature para saber qué versión invalidar
    stmt = select(Feature).where(Feature.id == feature_id)
    result = await self.session.execute(stmt)
    feature = result.scalar_one_or_none()

    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    version_id = feature.feature_model_version_id

    # 2. Eliminar de BD
    await self.session.delete(feature)
    await self.session.commit()

    # 3. NUEVO: Invalidar caché
    try:
        deleted_keys = await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
        logger.info(f"cache.invalidated: {deleted_keys} keys for version {version_id}")
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")
        # Continuar sin fallar (graceful degradation)
```

---

## 📝 Ejemplo 2: Invalidar al actualizar una Feature

**Archivo:** `backend/app/repositories/feature.py`

```python
async def update_feature(
    self,
    feature_id: uuid.UUID,
    update_data: dict
) -> Feature:
    """Actualizar una feature e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    # 1. Obtener feature actual
    feature = await self.get(feature_id)
    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    version_id = feature.feature_model_version_id

    # 2. Actualizar en BD
    for key, value in update_data.items():
        setattr(feature, key, value)

    self.session.add(feature)
    await self.session.commit()

    # 3. NUEVO: Invalidar caché
    try:
        deleted_keys = await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
        logger.info(f"cache.invalidated: {deleted_keys} keys for version {version_id}")
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return feature
```

---

## 📝 Ejemplo 3: Invalidar al crear Feature

**Archivo:** `backend/app/repositories/feature.py`

```python
async def create_feature(
    self,
    feature_create: FeatureCreate
) -> Feature:
    """Crear una feature e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    # 1. Crear feature
    feature = Feature(**feature_create.dict())
    self.session.add(feature)
    await self.session.flush()
    await self.session.commit()

    version_id = feature.feature_model_version_id

    # 2. NUEVO: Invalidar caché
    try:
        deleted_keys = await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
        logger.info(f"cache.invalidated: {deleted_keys} keys for version {version_id}")
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return feature
```

---

## 📝 Ejemplo 4: Invalidar Constraint

**Archivo:** `backend/app/repositories/constraint.py`

```python
async def create_constraint(
    self,
    constraint_create: ConstraintCreate
) -> Constraint:
    """Crear un constraint e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    constraint = Constraint(**constraint_create.dict())
    self.session.add(constraint)
    await self.session.flush()
    await self.session.commit()

    version_id = constraint.feature_model_version_id

    # Invalidar caché de la versión
    try:
        await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return constraint

async def delete_constraint(self, constraint_id: uuid.UUID) -> None:
    """Eliminar constraint e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    constraint = await self.get(constraint_id)
    if not constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))

    version_id = constraint.feature_model_version_id

    await self.session.delete(constraint)
    await self.session.commit()

    try:
        await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")
```

---

## 📝 Ejemplo 5: Invalidar Feature Relation

**Archivo:** `backend/app/repositories/feature_relation.py`

```python
async def create_feature_relation(
    self,
    relation_create: FeatureRelationCreate
) -> FeatureRelation:
    """Crear relación e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    relation = FeatureRelation(**relation_create.dict())
    self.session.add(relation)
    await self.session.flush()
    await self.session.commit()

    version_id = relation.feature_model_version_id

    try:
        await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return relation

async def delete_feature_relation(self, relation_id: uuid.UUID) -> None:
    """Eliminar relación e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    relation = await self.get(relation_id)
    if not relation:
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))

    version_id = relation.feature_model_version_id

    await self.session.delete(relation)
    await self.session.commit()

    try:
        await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")
```

---

## 📝 Ejemplo 6: Invalidar Feature Group

**Archivo:** `backend/app/repositories/feature_group.py`

```python
async def update_feature_group(
    self,
    group_id: uuid.UUID,
    update_data: dict
) -> FeatureGroup:
    """Actualizar grupo e invalidar caché."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    group = await self.get(group_id)
    if not group:
        raise FeatureGroupNotFoundException(group_id=str(group_id))

    version_id = group.feature_model_version_id

    for key, value in update_data.items():
        setattr(group, key, value)

    self.session.add(group)
    await self.session.commit()

    try:
        await CacheKeys.invalidate_version_cache(
            version_id=version_id,
            redis_client=redis_client
        )
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return group
```

---

## 📝 Ejemplo 7: Invalidar Versión Completa

**Archivo:** `backend/app/repositories/feature_model_version.py`

```python
async def publish_version(
    self,
    version_id: uuid.UUID
) -> FeatureModelVersion:
    """Publicar versión e invalidar caché del modelo."""
    from app.core.redis import redis_client
    from app.core.cache import CacheKeys

    version = await self.get(version_id)
    if not version:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    # Cambiar status a PUBLISHED
    version.status = ModelStatus.PUBLISHED
    self.session.add(version)
    await self.session.commit()

    # Invalidar TODO el modelo (todas las versiones + exportaciones)
    try:
        deleted_keys = await CacheKeys.invalidate_model_cache(
            model_id=version.feature_model_id,
            redis_client=redis_client,
            include_all_versions=True
        )
        logger.info(f"cache.invalidated_full_model: {deleted_keys} keys")
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return version
```

---

## 🎯 Patrón General

Todos los ejemplos siguen este patrón:

```python
async def write_operation(self, ...):
    """Operación que modifica datos."""

    # 1. Obtener información necesaria para invalidación
    entity = await self.get(entity_id)
    version_id = entity.feature_model_version_id  # o model_id

    # 2. Realizar operación en BD
    # ... create/update/delete ...

    # 3. Invalidar caché (TRY-EXCEPT para graceful degradation)
    try:
        from app.core.redis import redis_client
        from app.core.cache import CacheKeys

        if operation_affects_tree:
            await CacheKeys.invalidate_version_cache(version_id, redis_client)
        elif operation_affects_model:
            await CacheKeys.invalidate_model_cache(model_id, redis_client)
    except Exception as e:
        logger.warning(f"cache.invalidation_failed: {str(e)}")

    return entity
```

---

## ✅ Checklist de Integración

- [ ] Agregar invalidación en `feature.py` - create, update, delete
- [ ] Agregar invalidación en `constraint.py` - create, update, delete
- [ ] Agregar invalidación en `feature_relation.py` - create, update, delete
- [ ] Agregar invalidación en `feature_group.py` - create, update, delete
- [ ] Agregar invalidación en `feature_model_version.py` - publish, archive
- [ ] Agregar invalidación en servicios que modifican datos
- [ ] Validar que redis_client está disponible en cada archivo
- [ ] Validar que logger está configurado
- [ ] Tests: verificar que caché se invalida después de write

---

## 🧪 Validación

Después de integrar, validar con:

```bash
# 1. Verificar que invalidación funciona
redis-cli FLUSHDB  # Limpiar caché

# 2. Hacer operación de lectura (cache MISS)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/feature-models/{id}/versions/{vid}/complete

redis-cli KEYS "tree:*"
# Should show: 1 key

# 3. Hacer operación de escritura (ej: crear feature)
curl -X POST http://localhost:8000/api/v1/features \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Feature", ...}'

redis-cli KEYS "tree:*"
# Should show: 0 keys (invalidado)

# 4. Hacer lectura nuevamente (rebuild cache)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/feature-models/{id}/versions/{vid}/complete

redis-cli KEYS "tree:*"
# Should show: 1 key (nuevo caché)
```

---

## 📞 Support

Si encuentras problemas:

1. **Verificar redis-cli:**

   ```bash
   redis-cli ping
   redis-cli INFO stats
   ```

2. **Verificar logs:**

   ```bash
   tail -f backend/logs/app.log | grep cache
   ```

3. **Verificar imports:**
   ```bash
   grep -r "from app.core.redis" backend/app/repositories/
   grep -r "from app.core.cache" backend/app/repositories/
   ```
