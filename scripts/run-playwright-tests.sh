#!/bin/bash

# Script para ejecutar tests de Playwright en Docker
# Uso: ./run-playwright-tests.sh [opciones]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Función para mostrar uso
show_usage() {
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  all           - Ejecutar todos los tests (default)"
    echo "  ui            - Ejecutar tests en modo UI"
    echo "  headed        - Ejecutar tests con navegador visible"
    echo "  debug         - Ejecutar tests en modo debug"
    echo "  report        - Mostrar el último reporte de tests"
    echo "  codegen       - Iniciar Playwright Codegen para grabar tests"
    echo "  install       - Reinstalar dependencias y navegadores"
    echo "  shell         - Abrir una shell en el contenedor de Playwright"
    echo "  <test-file>   - Ejecutar un archivo de test específico"
    echo ""
    echo "Ejemplos:"
    echo "  $0 all                    # Todos los tests"
    echo "  $0 tests/login.spec.ts   # Test específico"
    echo "  $0 ui                     # Modo UI interactivo"
    echo "  $0 report                 # Ver reporte"
}

# Función para verificar que el contenedor está corriendo
check_container() {
    if ! docker compose -f docker-compose.dev.yml ps playwright | grep -q "Up\|running"; then
        echo -e "${YELLOW}⚠️  Contenedor de Playwright no está corriendo${NC}"
        echo -e "${BLUE}Iniciando contenedor...${NC}"
        docker compose -f docker-compose.dev.yml up -d playwright
        echo -e "${GREEN}✅ Contenedor iniciado${NC}"
        echo ""
        # Esperar a que esté healthy
        echo -e "${BLUE}Esperando health check...${NC}"
        sleep 5
    fi
}

# Verificar argumentos
MODE="${1:-all}"

case "$MODE" in
    help|--help|-h)
        show_usage
        exit 0
        ;;
    
    all)
        echo -e "${BLUE}🎭 Ejecutando todos los tests de Playwright...${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright test
        ;;
    
    ui)
        echo -e "${BLUE}🎭 Iniciando Playwright en modo UI...${NC}"
        echo -e "${YELLOW}Nota: El modo UI requiere X11 forwarding o ejecutar localmente${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright test --ui
        ;;
    
    headed)
        echo -e "${BLUE}🎭 Ejecutando tests con navegador visible...${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright test --headed
        ;;
    
    debug)
        echo -e "${BLUE}🎭 Ejecutando tests en modo debug...${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright test --debug
        ;;
    
    report)
        echo -e "${BLUE}📊 Abriendo reporte de tests...${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright show-report
        echo ""
        echo -e "${GREEN}💡 También puedes ver el reporte en:${NC}"
        echo -e "   ${BLUE}file://$SCRIPT_DIR/frontend/playwright-report/index.html${NC}"
        ;;
    
    codegen)
        echo -e "${BLUE}🎬 Iniciando Playwright Codegen...${NC}"
        URL="${2:-http://frontend:5173}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright codegen "$URL"
        ;;
    
    install)
        echo -e "${BLUE}📦 Reinstalando dependencias y navegadores...${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npm install
        docker compose -f docker-compose.dev.yml exec playwright npx playwright install --with-deps
        echo -e "${GREEN}✅ Instalación completada${NC}"
        ;;
    
    shell)
        echo -e "${BLUE}🐚 Abriendo shell en el contenedor de Playwright...${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright /bin/bash
        ;;
    
    clean)
        echo -e "${BLUE}🧹 Limpiando resultados de tests anteriores...${NC}"
        rm -rf frontend/test-results frontend/playwright-report
        echo -e "${GREEN}✅ Limpieza completada${NC}"
        ;;
    
    *.spec.ts|*.spec.js|tests/*)
        echo -e "${BLUE}🎭 Ejecutando test específico: $MODE${NC}"
        check_container
        docker compose -f docker-compose.dev.yml exec playwright npx playwright test "$MODE"
        ;;
    
    *)
        echo -e "${RED}❌ Opción no reconocida: $MODE${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac

# Mostrar status al final
echo ""
echo -e "${GREEN}✅ Comando completado${NC}"
echo ""
echo -e "${BLUE}📝 Comandos útiles:${NC}"
echo -e "  Ver logs:    docker compose -f docker-compose.dev.yml logs playwright"
echo -e "  Ver reporte: ./run-playwright-tests.sh report"
echo -e "  Limpiar:     ./run-playwright-tests.sh clean"
