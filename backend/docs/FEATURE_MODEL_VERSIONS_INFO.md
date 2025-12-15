# 📊 Información de Versiones en Endpoints de Feature Models

## 🎯 Cambios Implementados

Se ha agregado información de versiones a los endpoints de listar y obtener detalles de feature models.

## 📡 Endpoints Actualizados

### 1. Listar Feature Models - `GET /api/v1/feature-models/`

**Nuevos campos agregados**:

- `versions_count`: Número total de versiones del feature model
- `latest_version`: Información de la última versión (la más reciente)
  - `id`: UUID de la versión
  - `version_number`: Número de versión
  - `status`: Estado de la versión (DRAFT, IN_REVIEW, PUBLISHED)

**Ejemplo de Respuesta**:

```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Plan de Estudios ICI",
      "owner_id": "user-uuid",
      "domain_id": "domain-uuid",
      "domain_name": "Ingeniería Informática",
      "created_at": "2025-11-24T06:36:26.897923",
      "updated_at": "2025-12-10T15:30:00.000000",
      "is_active": true,
      "versions_count": 3,
      "latest_version": {
        "id": "version-uuid-3",
        "version_number": 3,
        "status": "PUBLISHED"
      }
    },
    {
      "id": "another-uuid",
      "name": "Modelo E-commerce",
      "owner_id": "user-uuid",
      "domain_id": "domain-uuid",
      "domain_name": "Comercio Electrónico",
      "created_at": "2025-12-01T10:00:00.000000",
      "updated_at": "2025-12-05T14:20:00.000000",
      "is_active": true,
      "versions_count": 1,
      "latest_version": {
        "id": "version-uuid-1",
        "version_number": 1,
        "status": "DRAFT"
      }
    }
  ],
  "count": 2,
  "page": 1,
  "size": 2,
  "total_pages": 1,
  "has_next": false,
  "has_prev": false
}
```

**Caso especial**: Si un feature model no tiene versiones:

```json
{
  "id": "new-model-uuid",
  "name": "Modelo Sin Versiones",
  "versions_count": 0,
  "latest_version": null
}
```

### 2. Obtener Feature Model - `GET /api/v1/feature-models/{model_id}/`

**Nuevos campos agregados**:

- `versions_count`: Número total de versiones del feature model
- `versions`: Lista completa de todas las versiones (ordenadas por `version_number`)
  - `id`: UUID de la versión
  - `version_number`: Número de versión
  - `status`: Estado de la versión (DRAFT, IN_REVIEW, PUBLISHED)
  - `created_at`: Fecha de creación de la versión

**Ejemplo de Respuesta**:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Plan de Estudios ICI",
  "description": "Modelo completo del plan de estudios de Ingeniería en Ciencias Informáticas",
  "owner_id": "user-uuid",
  "domain_id": "domain-uuid",
  "domain_name": "Ingeniería Informática",
  "created_at": "2025-11-24T06:36:26.897923",
  "updated_at": "2025-12-10T15:30:00.000000",
  "is_active": true,
  "versions_count": 3,
  "versions": [
    {
      "id": "version-uuid-1",
      "version_number": 1,
      "status": "PUBLISHED",
      "created_at": "2025-11-24T06:36:26.897923"
    },
    {
      "id": "version-uuid-2",
      "version_number": 2,
      "status": "PUBLISHED",
      "created_at": "2025-11-30T10:15:00.000000"
    },
    {
      "id": "version-uuid-3",
      "version_number": 3,
      "status": "DRAFT",
      "created_at": "2025-12-10T15:30:00.000000"
    }
  ]
}
```

## 🔄 Estados de Versiones

Las versiones pueden tener los siguientes estados:

| Estado      | Descripción                      |
| ----------- | -------------------------------- |
| `DRAFT`     | Versión en borrador, editable    |
| `IN_REVIEW` | Versión en revisión, no editable |
| `PUBLISHED` | Versión publicada, inmutable     |

## 📝 Notas de Implementación

### Optimizaciones

1. **Eager Loading**: Las versiones se cargan usando `selectinload` para evitar N+1 queries:

   ```python
   stmt = (
       select(FeatureModel)
       .options(
           selectinload(FeatureModel.domain),
           selectinload(FeatureModel.versions)
       )
   )
   ```

2. **Ordenamiento**:

   - En el listado: Se muestra solo la última versión (mayor `version_number`)
   - En el detalle: Se muestran todas las versiones ordenadas ascendentemente por `version_number`

3. **Schemas Separados**:
   - `LatestVersionInfo`: Solo ID, número y estado (para listados)
   - `VersionInfo`: Incluye también `created_at` (para detalles)

### Todos los Endpoints Afectados

Los siguientes endpoints ahora incluyen información de versiones:

✅ `GET /api/v1/feature-models/` - Listado (última versión)
✅ `GET /api/v1/feature-models/{model_id}/` - Detalle (todas las versiones)
✅ `POST /api/v1/feature-models/` - Crear (versiones del nuevo modelo)
✅ `PATCH /api/v1/feature-models/{model_id}/` - Actualizar (versiones actualizadas)
✅ `PATCH /api/v1/feature-models/{model_id}/activate/` - Activar (con versiones)
✅ `PATCH /api/v1/feature-models/{model_id}/deactivate/` - Desactivar (con versiones)

## 🎨 Casos de Uso en el Frontend

### 1. Mostrar Badge de Última Versión en el Listado

```typescript
interface FeatureModelListItem {
  id: string;
  name: string;
  versions_count: number;
  latest_version?: {
    id: string;
    version_number: number;
    status: string;
  };
}

function FeatureModelCard({ model }: { model: FeatureModelListItem }) {
  return (
    <div className="card">
      <h3>{model.name}</h3>
      {model.latest_version ? (
        <div className="version-info">
          <Badge status={model.latest_version.status}>
            v{model.latest_version.version_number}
          </Badge>
          <span>{model.versions_count} versiones</span>
        </div>
      ) : (
        <span className="text-muted">Sin versiones</span>
      )}
    </div>
  );
}
```

### 2. Selector de Versiones en Vista Detalle

```typescript
interface FeatureModelDetail {
  id: string;
  name: string;
  versions_count: number;
  versions: Array<{
    id: string;
    version_number: number;
    status: string;
    created_at: string;
  }>;
}

function VersionSelector({ model }: { model: FeatureModelDetail }) {
  const [selectedVersion, setSelectedVersion] = useState(
    model.versions[model.versions.length - 1] // Última versión por defecto
  );

  return (
    <select
      value={selectedVersion.id}
      onChange={(e) => {
        const version = model.versions.find((v) => v.id === e.target.value);
        setSelectedVersion(version);
      }}
    >
      {model.versions.map((version) => (
        <option key={version.id} value={version.id}>
          Versión {version.version_number} - {version.status} (
          {new Date(version.created_at).toLocaleDateString()})
        </option>
      ))}
    </select>
  );
}
```

### 3. Timeline de Versiones

```typescript
function VersionTimeline({ versions }: { versions: VersionInfo[] }) {
  return (
    <div className="timeline">
      {versions.map((version, index) => (
        <div key={version.id} className="timeline-item">
          <div className="timeline-marker">
            <span className="version-number">v{version.version_number}</span>
          </div>
          <div className="timeline-content">
            <Badge status={version.status}>{version.status}</Badge>
            <time>{new Date(version.created_at).toLocaleString()}</time>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## 🧪 Testing

### Probar el Endpoint de Listado

```bash
curl -X GET "http://localhost:8000/api/v1/feature-models/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Probar el Endpoint de Detalle

```bash
curl -X GET "http://localhost:8000/api/v1/feature-models/{model_id}/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ✅ Validaciones

- ✅ Las versiones siempre se cargan con eager loading (sin N+1 queries)
- ✅ En listados: Solo se muestra la última versión
- ✅ En detalles: Se muestran todas las versiones ordenadas
- ✅ Si no hay versiones: `versions_count=0` y `latest_version=null`
- ✅ El estado de las versiones se convierte de enum a string
- ✅ Compatible con caché (las versiones son parte de la respuesta cacheada)

## 🎉 Beneficios

1. **Visibilidad**: Los usuarios ven inmediatamente cuántas versiones tiene un modelo
2. **Contexto**: El listado muestra la versión más relevante (la última)
3. **Navegación**: El detalle permite ver todas las versiones para navegación
4. **Performance**: Eager loading optimizado, sin queries adicionales
5. **Frontend-friendly**: Información lista para renderizar selectores y timelines
