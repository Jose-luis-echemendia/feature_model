# ⚙️ API de Configuraciones

Documentación de los endpoints de configuraciones y estrategias de generación.

## 📡 Endpoints

### 1) Crear configuración (manual)

```http
POST /api/v1/configurations
```

**Body**

```json
{
  "name": "Config base",
  "description": "Selección inicial",
  "feature_model_version_id": "uuid",
  "feature_ids": ["uuid", "uuid"]
}
```

**Comportamiento**

- Valida la selección con el validador lógico.
- Si falla: 400 con `detail` = lista de errores.
- Si pasa: guarda la configuración.

### 2) Obtener configuración

```http
GET /api/v1/configurations/{id}
```

### 3) Listar configuraciones (paginado)

```http
GET /api/v1/configurations?skip=0&limit=100
```

### 4) Actualizar configuración

```http
PUT /api/v1/configurations/{id}
```

### 5) Eliminar configuración

```http
DELETE /api/v1/configurations/{id}
```

### 6) Validar configuración (sin persistir)

```http
POST /api/v1/configurations/validate
```

**Body**

```json
{
  "feature_model_version_id": "uuid",
  "selected_features": ["uuid", "uuid"]
}
```

### 7) Generar configuraciones

```http
POST /api/v1/configurations/generate
```

**Body**

```json
{
  "feature_model_version_id": "uuid",
  "strategy": "greedy",
  "count": 5,
  "diverse": true,
  "partial_selection": {
    "uuid": true,
    "uuid": false
  }
}
```

### 8) Staged configuration (opciones válidas)

```http
POST /api/v1/configurations/staged/options
```

**Body**

```json
{
  "feature_model_version_id": "uuid",
  "partial_selection": {
    "uuid": true,
    "uuid": false
  }
}
```

**Respuesta**

- `can_select`: features que pueden activarse
- `can_deselect`: features que pueden desactivarse
- `must_select`: features forzadas a activo
- `must_deselect`: features forzadas a inactivo

## 🎯 Estrategias de generación

- `greedy`: selección golosa determinista.
- `random`: selección aleatoria válida.
- `beam_search`: búsqueda en haz.
- `genetic`: heurística genética (DEAP).
- `sat_enum`: enumeración exacta con SAT/SMT.
- `pairwise`: cobertura T-wise (pares).
- `uniform`: muestreo uniforme aproximado.
- `stratified`: muestreo estratificado por tamaño.
- `cp_sat`: CP-SAT con OR-Tools.
- `bdd`: muestreo con BDD/ROBDD.
- `nsga2`: multiobjetivo (NSGA-II/MOEA).

## ✅ Notas

- Algunas estrategias dependen de librerías externas (DEAP, Z3, OR-Tools, dd).
- Las estrategias exactas pueden ser costosas en modelos grandes.
