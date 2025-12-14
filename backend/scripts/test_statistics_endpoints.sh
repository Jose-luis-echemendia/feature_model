#!/bin/bash

# Script para probar los endpoints de estadísticas

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Probando Endpoints de Estadísticas ===${NC}\n"

# Variables (ajustar según tus datos)
BASE_URL="http://127.0.0.1:8000/api/v1"
MODEL_ID="b4664b05-3159-40ce-ad04-7d00c7a24973"
VERSION_ID="tu-version-uuid-aqui"  # Reemplazar con UUID real
TOKEN="tu-token-aqui"  # Reemplazar con token real

echo -e "${YELLOW}Nota: Asegúrate de actualizar MODEL_ID, VERSION_ID y TOKEN en este script${NC}\n"

# Test 1: Estadísticas de última versión publicada
echo -e "${GREEN}Test 1: GET /versions/latest/statistics${NC}"
echo "URL: $BASE_URL/feature-models/$MODEL_ID/versions/latest/statistics"
echo ""

curl -s -X GET \
  "$BASE_URL/feature-models/$MODEL_ID/versions/latest/statistics" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP Status: %{http_code}\n" | jq '.'

echo -e "\n---\n"

# Test 2: Estadísticas de una versión específica
echo -e "${GREEN}Test 2: GET /versions/{version_id}/statistics${NC}"
echo "URL: $BASE_URL/feature-models/$MODEL_ID/versions/$VERSION_ID/statistics"
echo ""

curl -s -X GET \
  "$BASE_URL/feature-models/$MODEL_ID/versions/$VERSION_ID/statistics" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP Status: %{http_code}\n" | jq '.'

echo -e "\n---\n"

echo -e "${GREEN}✅ Tests completados${NC}"
echo ""
echo -e "${YELLOW}Respuestas esperadas:${NC}"
echo "  - HTTP 200 con JSON de estadísticas"
echo "  - Campos: total_features, mandatory_features, optional_features, etc."
echo ""
echo -e "${YELLOW}Errores comunes:${NC}"
echo "  - HTTP 404: Feature model o versión no encontrada"
echo "  - HTTP 401: Token inválido o faltante"
echo "  - HTTP 422: UUID inválido (si aún hay problemas de orden de rutas)"
