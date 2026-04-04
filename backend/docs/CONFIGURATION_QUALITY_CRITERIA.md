# ✅ Criterios de Calidad para Configuraciones

Esta guía define métricas y criterios para evaluar la calidad de configuraciones generadas.

## 1) Diversidad

**Objetivo:** evitar configuraciones demasiado similares.

**Métricas sugeridas:**
- Distancia de Jaccard entre configuraciones seleccionadas.
- Cobertura de features poco frecuentes.

**Criterio mínimo:**
- Distancia Jaccard promedio ≥ 0.3 (ajustable por dominio).

## 2) Cobertura

**Objetivo:** cubrir interacciones relevantes entre features.

**Métricas sugeridas:**
- **Pairwise (2-wise):** porcentaje de pares cubiertos.
- **T-wise:** porcentaje de combinaciones de tamaño T cubiertas.

**Criterio mínimo:**
- Cobertura pairwise ≥ 80% para lotes pequeños.

## 3) Objetivos (optimización)

**Objetivo:** maximizar o minimizar propiedades específicas.

**Ejemplos:**
- Maximizar número de features seleccionadas.
- Minimizar coste total.
- Balancear carga académica o complejidad.

**Criterio mínimo:**
- Reportar valores de objetivo por configuración.
- Mantener configuraciones válidas (0 violaciones).

## 4) Validez

**Objetivo:** todas las configuraciones deben satisfacer constraints.

**Criterio mínimo:**
- Tasa de validez = 100% en resultados finales.

## 5) Rendimiento

**Objetivo:** asegurar tiempos aceptables de generación.

**Métricas sugeridas:**
- Tiempo medio por configuración.
- Tiempo máximo para lote.

**Criterio mínimo:**
- < 2s por configuración en modelos medianos (ajustable).

## 6) Estabilidad

**Objetivo:** evitar fluctuaciones grandes entre ejecuciones.

**Métricas sugeridas:**
- Desviación estándar del tamaño de configuraciones.

**Criterio mínimo:**
- Desviación bajo umbral definido por dominio.
