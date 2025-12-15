# 📊 API de Estadísticas en Tiempo Real para Feature Models

## 🎯 Objetivo

Proporcionar estadísticas actualizadas en tiempo real sobre feature models para:

- **Dashboards interactivos** con métricas visuales
- **Validación de complejidad** antes de publicar
- **Monitoreo durante edición** para feedback inmediato
- **Reportes y análisis** de modelos

## 📡 Endpoints Disponibles

### 1. Estadísticas de una Versión Específica

```http
GET /api/v1/feature-models/{model_id}/versions/{version_id}/statistics
```

**Descripción**: Obtiene estadísticas en tiempo real de una versión específica.

**Parámetros**:

- `model_id` (UUID): ID del feature model
- `version_id` (UUID): ID de la versión específica

**Headers**:

```
Authorization: Bearer {token}
```

**Respuesta** (200 OK):

```json
{
  "total_features": 45,
  "mandatory_features": 32,
  "optional_features": 13,
  "total_groups": 5,
  "xor_groups": 3,
  "or_groups": 2,
  "total_relations": 18,
  "requires_relations": 15,
  "excludes_relations": 3,
  "total_constraints": 8,
  "total_configurations": 12,
  "max_tree_depth": 5
}
```

### 2. Estadísticas de la Última Versión Publicada

```http
GET /api/v1/feature-models/{model_id}/versions/latest/statistics
```

**Descripción**: Atajo para obtener estadísticas de la última versión PUBLISHED.

**Parámetros**:

- `model_id` (UUID): ID del feature model

**Respuesta**: Misma estructura que el endpoint anterior

**Nota**: Solo considera versiones con estado `PUBLISHED`. Retorna 404 si no hay versiones publicadas.

## 📊 Campos de las Estadísticas

| Campo                  | Tipo | Descripción                                  |
| ---------------------- | ---- | -------------------------------------------- |
| `total_features`       | int  | Total de features en el modelo               |
| `mandatory_features`   | int  | Features obligatorias (MANDATORY)            |
| `optional_features`    | int  | Features opcionales (OPTIONAL)               |
| `total_groups`         | int  | Total de grupos (XOR + OR)                   |
| `xor_groups`           | int  | Grupos XOR (elegir exactamente una)          |
| `or_groups`            | int  | Grupos OR (elegir una o más)                 |
| `total_relations`      | int  | Total de relaciones entre features           |
| `requires_relations`   | int  | Relaciones de prerequisito (A requiere B)    |
| `excludes_relations`   | int  | Relaciones de exclusión (A excluye B)        |
| `total_constraints`    | int  | Restricciones formales del modelo            |
| `total_configurations` | int  | Configuraciones válidas generadas            |
| `max_tree_depth`       | int  | Profundidad máxima del árbol (0 = solo raíz) |

## 🚀 Performance

| Tamaño del Modelo          | Tiempo de Respuesta |
| -------------------------- | ------------------- |
| Pequeño (<100 features)    | ~50-100ms           |
| Mediano (100-500 features) | ~100-300ms          |
| Grande (>500 features)     | ~300-800ms          |

**Nota**: Las estadísticas se calculan en tiempo real (no cacheadas) para garantizar datos actualizados.

## 💡 Casos de Uso

### 1. Dashboard en el Frontend

```typescript
interface Statistics {
  total_features: number;
  mandatory_features: number;
  optional_features: number;
  total_groups: number;
  xor_groups: number;
  or_groups: number;
  total_relations: number;
  requires_relations: number;
  excludes_relations: number;
  total_constraints: number;
  total_configurations: number;
  max_tree_depth: number;
}

async function loadStatistics(
  modelId: string,
  versionId: string
): Promise<Statistics> {
  const response = await fetch(
    `/api/v1/feature-models/${modelId}/versions/${versionId}/statistics`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load statistics");
  }

  return response.json();
}

// Dashboard Component
function StatisticsDashboard() {
  const [stats, setStats] = useState<Statistics | null>(null);

  useEffect(() => {
    async function fetchStats() {
      const data = await loadStatistics(modelId, versionId);
      setStats(data);
    }
    fetchStats();
  }, [modelId, versionId]);

  if (!stats) return <Loading />;

  return (
    <div className="grid grid-cols-3 gap-4">
      <StatCard title="Total Features" value={stats.total_features} icon="📦" />
      <StatCard
        title="Mandatory"
        value={stats.mandatory_features}
        percentage={Math.round(
          (stats.mandatory_features / stats.total_features) * 100
        )}
        icon="✅"
      />
      <StatCard
        title="Optional"
        value={stats.optional_features}
        percentage={Math.round(
          (stats.optional_features / stats.total_features) * 100
        )}
        icon="🔄"
      />
      <StatCard
        title="Groups"
        value={stats.total_groups}
        subtitle={`${stats.xor_groups} XOR, ${stats.or_groups} OR`}
        icon="👥"
      />
      <StatCard
        title="Relations"
        value={stats.total_relations}
        subtitle={`${stats.requires_relations} requires, ${stats.excludes_relations} excludes`}
        icon="🔗"
      />
      <StatCard title="Tree Depth" value={stats.max_tree_depth} icon="🌳" />
    </div>
  );
}
```

### 2. Actualización en Tiempo Real Durante Edición

```typescript
// Hook personalizado para polling de estadísticas
function useRealtimeStatistics(
  modelId: string,
  versionId: string,
  intervalMs: number = 5000
) {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    async function fetchStats() {
      try {
        const data = await loadStatistics(modelId, versionId);
        setStats(data);
        setIsLoading(false);
      } catch (error) {
        console.error("Error loading statistics:", error);
      }
    }

    // Carga inicial
    fetchStats();

    // Polling cada X segundos
    intervalId = setInterval(fetchStats, intervalMs);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [modelId, versionId, intervalMs]);

  return { stats, isLoading };
}

// Componente que se actualiza automáticamente
function LiveStatisticsBadge() {
  const { stats, isLoading } = useRealtimeStatistics(modelId, versionId, 5000);

  return (
    <div className="live-stats-badge">
      {isLoading ? (
        <Spinner size="sm" />
      ) : (
        <>
          <div className="pulse-indicator"></div>
          <span>{stats?.total_features} features</span>
          <span>·</span>
          <span>Depth: {stats?.max_tree_depth}</span>
        </>
      )}
    </div>
  );
}
```

### 3. Validación Antes de Publicar

```typescript
async function validateBeforePublish(
  modelId: string,
  versionId: string
): Promise<{ valid: boolean; issues: string[] }> {
  const stats = await loadStatistics(modelId, versionId);
  const issues: string[] = [];

  // Validaciones de complejidad
  if (stats.total_features === 0) {
    issues.push("El modelo no tiene features");
  }

  if (stats.total_features > 1000) {
    issues.push(
      "El modelo es muy grande (>1000 features). Considera dividirlo."
    );
  }

  if (stats.max_tree_depth > 10) {
    issues.push(
      "El árbol es muy profundo (>10 niveles). Puede ser difícil de mantener."
    );
  }

  if (stats.mandatory_features === 0 && stats.total_features > 0) {
    issues.push("No hay features obligatorias definidas");
  }

  // Validación de relaciones
  const relationDensity =
    stats.total_relations / Math.max(stats.total_features, 1);
  if (relationDensity > 2) {
    issues.push(
      "Demasiadas relaciones por feature. El modelo puede ser muy acoplado."
    );
  }

  return {
    valid: issues.length === 0,
    issues,
  };
}

// Componente de validación
function PublishValidation() {
  const [validation, setValidation] = useState<{
    valid: boolean;
    issues: string[];
  } | null>(null);

  async function handleValidate() {
    const result = await validateBeforePublish(modelId, versionId);
    setValidation(result);
  }

  return (
    <div>
      <button onClick={handleValidate}>Validar Antes de Publicar</button>

      {validation && (
        <div className={validation.valid ? "success" : "warning"}>
          {validation.valid ? (
            <p>✅ El modelo está listo para publicarse</p>
          ) : (
            <div>
              <p>⚠️ Se encontraron {validation.issues.length} problemas:</p>
              <ul>
                {validation.issues.map((issue, i) => (
                  <li key={i}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 4. Gráficos de Distribución

```typescript
import { Pie, Bar } from "react-chartjs-2";

function StatisticsCharts({ stats }: { stats: Statistics }) {
  // Gráfico de pastel: Mandatory vs Optional
  const featureTypeData = {
    labels: ["Mandatory", "Optional"],
    datasets: [
      {
        data: [stats.mandatory_features, stats.optional_features],
        backgroundColor: ["#4CAF50", "#FFC107"],
      },
    ],
  };

  // Gráfico de barras: Grupos por tipo
  const groupTypeData = {
    labels: ["XOR Groups", "OR Groups"],
    datasets: [
      {
        label: "Count",
        data: [stats.xor_groups, stats.or_groups],
        backgroundColor: ["#2196F3", "#9C27B0"],
      },
    ],
  };

  // Gráfico de barras: Relaciones por tipo
  const relationTypeData = {
    labels: ["Requires", "Excludes"],
    datasets: [
      {
        label: "Count",
        data: [stats.requires_relations, stats.excludes_relations],
        backgroundColor: ["#4CAF50", "#F44336"],
      },
    ],
  };

  return (
    <div className="charts-grid">
      <div className="chart-container">
        <h3>Feature Types</h3>
        <Pie data={featureTypeData} />
      </div>

      <div className="chart-container">
        <h3>Groups by Type</h3>
        <Bar data={groupTypeData} />
      </div>

      <div className="chart-container">
        <h3>Relations by Type</h3>
        <Bar data={relationTypeData} />
      </div>
    </div>
  );
}
```

### 5. Comparación de Versiones

```typescript
async function compareVersions(
  modelId: string,
  version1Id: string,
  version2Id: string
) {
  const [stats1, stats2] = await Promise.all([
    loadStatistics(modelId, version1Id),
    loadStatistics(modelId, version2Id),
  ]);

  return {
    total_features_diff: stats2.total_features - stats1.total_features,
    mandatory_features_diff:
      stats2.mandatory_features - stats1.mandatory_features,
    optional_features_diff: stats2.optional_features - stats1.optional_features,
    total_groups_diff: stats2.total_groups - stats1.total_groups,
    total_relations_diff: stats2.total_relations - stats1.total_relations,
    max_tree_depth_diff: stats2.max_tree_depth - stats1.max_tree_depth,
  };
}

function VersionComparison() {
  const [comparison, setComparison] = useState<any>(null);

  useEffect(() => {
    async function compare() {
      const diff = await compareVersions(modelId, version1Id, version2Id);
      setComparison(diff);
    }
    compare();
  }, [version1Id, version2Id]);

  if (!comparison) return <Loading />;

  return (
    <div className="comparison-table">
      <h3>
        Changes from v{version1Number} to v{version2Number}
      </h3>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Change</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(comparison).map(([key, value]) => (
            <tr key={key}>
              <td>{formatMetricName(key)}</td>
              <td
                className={
                  value > 0 ? "positive" : value < 0 ? "negative" : "neutral"
                }
              >
                {value > 0 ? "+" : ""}
                {value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## ⚡ Optimizaciones

### 1. Caché en el Frontend

```typescript
// Cachear estadísticas por 30 segundos
const statisticsCache = new Map<
  string,
  { data: Statistics; timestamp: number }
>();
const CACHE_TTL = 30000; // 30 segundos

async function loadStatisticsCached(
  modelId: string,
  versionId: string
): Promise<Statistics> {
  const cacheKey = `${modelId}-${versionId}`;
  const cached = statisticsCache.get(cacheKey);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const data = await loadStatistics(modelId, versionId);
  statisticsCache.set(cacheKey, { data, timestamp: Date.now() });

  return data;
}
```

### 2. Debounce para Actualizaciones Frecuentes

```typescript
import { debounce } from "lodash";

// Actualizar estadísticas solo después de 2 segundos de inactividad
const debouncedRefresh = debounce(
  async (modelId: string, versionId: string) => {
    const stats = await loadStatistics(modelId, versionId);
    setStats(stats);
  },
  2000
);

// Llamar después de cada edición
function handleFeatureAdded() {
  // ... lógica de agregar feature
  debouncedRefresh(modelId, versionId);
}
```

## 🧪 Testing

```bash
# Obtener estadísticas de una versión específica
curl -X GET "http://localhost:8000/api/v1/feature-models/{model_id}/versions/{version_id}/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Obtener estadísticas de la última versión publicada
curl -X GET "http://localhost:8000/api/v1/feature-models/{model_id}/versions/latest/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ✅ Beneficios

1. **🔄 Tiempo Real**: Las estadísticas siempre reflejan el estado actual
2. **📊 Dashboard Rico**: Métricas visuales para análisis
3. **⚡ Rápido**: Optimizado para respuestas <300ms en modelos típicos
4. **🎯 Validación**: Detecta problemas antes de publicar
5. **📈 Monitoreo**: Tracking de complejidad durante edición
6. **🔍 Comparación**: Analiza diferencias entre versiones

## 🔮 Mejoras Futuras

1. **WebSocket para Push**: Enviar actualizaciones automáticas al frontend
2. **Historial de Estadísticas**: Guardar snapshots para análisis temporal
3. **Alertas Personalizables**: Notificar cuando métricas exceden umbrales
4. **Export a CSV/Excel**: Descargar reportes de estadísticas
5. **Machine Learning**: Predecir complejidad futura basándose en tendencias

## 📝 Notas Importantes

- ⚠️ **Sin Caché**: Este endpoint NO usa caché para garantizar datos en tiempo real
- 🔒 **Autenticación Requerida**: Token JWT necesario
- ✅ **Solo Modelos Activos**: Retorna 400 si el modelo está desactivado
- 📊 **Versiones Publicadas**: El endpoint `/latest/statistics` solo considera versiones PUBLISHED
