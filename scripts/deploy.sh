#!/bin/bash

# ════════════════════════════════════════════════════════════════════════════
# Script de Despliegue Unificado - Feature Models Platform
# ════════════════════════════════════════════════════════════════════════════
# 
# Este script integra dos modos de despliegue:
#   1. Despliegue interactivo con menú (por defecto)
#   2. Despliegue Docker Swarm (modo --swarm)
#
# Uso:
#   ./scripts/deploy.sh              # Modo interactivo
#   ./scripts/deploy.sh --swarm      # Modo Docker Swarm
#
# ════════════════════════════════════════════════════════════════════════════

set -e

# ============================================================================
# CONFIGURACIÓN Y COLORES
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

print_header() {
    echo -e "${CYAN}"
    echo "════════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Cargar variables de entorno
load_env() {
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        print_success "Variables de entorno cargadas"
    else
        print_error "Archivo .env no encontrado"
        exit 1
    fi
}

# ============================================================================
# FUNCIONES DOCKER SWARM
# ============================================================================

deploy_swarm() {
    print_header "🐳 DESPLIEGUE DOCKER SWARM"
    
    # Validar variables requeridas
    if [ -z "$DOMAIN" ]; then
        print_error "Variable DOMAIN no configurada"
        exit 1
    fi
    
    if [ -z "$STACK_NAME" ]; then
        print_error "Variable STACK_NAME no configurada"
        exit 1
    fi
    
    if [ -z "$TAG" ]; then
        print_warning "Variable TAG no configurada, usando 'latest'"
        TAG="latest"
    fi
    
    print_info "Domain: $DOMAIN"
    print_info "Stack: $STACK_NAME"
    print_info "Tag: $TAG"
    
    # Generar configuración de docker-stack
    print_info "Generando docker-stack.yml..."
    DOMAIN=$DOMAIN \
    STACK_NAME=$STACK_NAME \
    TAG=$TAG \
    docker-compose \
    -f docker-compose.prod.yml \
    config > docker-stack.yml
    
    # Aplicar auto-labels (si está disponible)
    if command -v docker-auto-labels &> /dev/null; then
        print_info "Aplicando auto-labels..."
        docker-auto-labels docker-stack.yml
    else
        print_warning "docker-auto-labels no encontrado, continuando sin labels automáticos"
    fi
    
    # Desplegar stack
    print_info "Desplegando stack en Swarm..."
    docker stack deploy -c docker-stack.yml --with-registry-auth "$STACK_NAME"
    
    print_success "Stack desplegado exitosamente"
    
    # Mostrar servicios
    echo ""
    print_info "Servicios desplegados:"
    docker stack services "$STACK_NAME"
}

# ============================================================================
# FUNCIONES DE BUILD
# ============================================================================

build_backend() {
    print_header "📦 CONSTRUYENDO BACKEND"
    
    local tag="${TAG:-latest}"
    local image="${DOCKER_IMAGE_BACKEND:-feature-models-backend}"
    
    print_info "Imagen: $image:$tag"
    
    docker build -t "$image:$tag" ./backend
    
    print_success "Backend construido: $image:$tag"
}

build_frontend() {
    print_header "📦 CONSTRUYENDO FRONTEND"
    
    local tag="${TAG:-latest}"
    local image="${DOCKER_IMAGE_FRONTEND:-feature-models-frontend}"
    local api_url="${VITE_API_URL:-https://api.${DOMAIN}}"
    
    print_info "Imagen: $image:$tag"
    print_info "API URL: $api_url"
    
    docker build -t "$image:$tag" \
        --build-arg VITE_API_URL="$api_url" \
        --build-arg NODE_ENV=production \
        ./frontend
    
    print_success "Frontend construido: $image:$tag"
}

build_all() {
    build_backend
    echo ""
    build_frontend
}

# ============================================================================
# FUNCIONES DE DESPLIEGUE
# ============================================================================

deploy_compose() {
    print_header "🚀 DESPLEGANDO SERVICIOS (Docker Compose)"
    
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Servicios desplegados"
}

redeploy() {
    print_header "🔄 REDESPLIEGUE COMPLETO"
    
    print_info "Deteniendo servicios..."
    docker-compose -f docker-compose.prod.yml down
    
    print_info "Iniciando servicios..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Redespliegue completado"
}

update_services() {
    print_header "⬆️  ACTUALIZANDO SERVICIOS"
    
    print_info "Descargando imágenes actualizadas..."
    docker-compose -f docker-compose.prod.yml pull
    
    print_info "Desplegando servicios..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Servicios actualizados"
}

# ============================================================================
# FUNCIONES DE MONITOREO
# ============================================================================

view_logs() {
    local service=$1
    
    print_header "📋 LOGS DE SERVICIOS"
    
    if [ -z "$service" ]; then
        print_info "Mostrando logs de todos los servicios..."
        docker-compose -f docker-compose.prod.yml logs -f
    else
        print_info "Mostrando logs de: $service"
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    fi
}

show_status() {
    print_header "📊 ESTADO DE SERVICIOS"
    
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    print_info "Uso de recursos:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
        $(docker-compose -f docker-compose.prod.yml ps -q)
}

# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

run_migrations() {
    print_header "🔄 EJECUTANDO MIGRACIONES"
    
    docker-compose -f docker-compose.prod.yml exec feature_models_backend alembic upgrade head
    
    print_success "Migraciones completadas"
}

create_superuser() {
    print_header "👤 CREANDO SUPERUSUARIO"
    
    docker-compose -f docker-compose.prod.yml exec feature_models_backend python -m app.initial_data
    
    print_success "Superusuario creado"
}

backup_database() {
    print_header "💾 BACKUP DE BASE DE DATOS"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backups/backup_${timestamp}.sql"
    
    # Crear directorio de backups si no existe
    mkdir -p backups
    
    print_info "Creando backup: $backup_file"
    
    docker-compose -f docker-compose.prod.yml exec -T db \
        pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" > "$backup_file"
    
    # Comprimir backup
    print_info "Comprimiendo backup..."
    gzip "$backup_file"
    
    print_success "Backup creado: ${backup_file}.gz"
    
    # Mostrar tamaño
    local size=$(du -h "${backup_file}.gz" | cut -f1)
    print_info "Tamaño: $size"
}

restore_database() {
    print_header "📥 RESTAURAR BASE DE DATOS"
    
    echo -e "${RED}"
    echo "⚠️  ADVERTENCIA: Esta operación sobrescribirá la base de datos actual"
    echo -e "${NC}"
    
    echo -n "¿Continuar? (escribe 'SI' para confirmar): "
    read confirmation
    
    if [ "$confirmation" != "SI" ]; then
        print_warning "Operación cancelada"
        return
    fi
    
    echo ""
    echo "Archivos de backup disponibles:"
    ls -lh backups/
    echo ""
    echo -n "Nombre del archivo a restaurar: "
    read backup_file
    
    if [ ! -f "$backup_file" ]; then
        print_error "Archivo no encontrado: $backup_file"
        return
    fi
    
    print_info "Restaurando desde: $backup_file"
    
    # Descomprimir si es necesario
    if [[ "$backup_file" == *.gz ]]; then
        print_info "Descomprimiendo..."
        gunzip -k "$backup_file"
        backup_file="${backup_file%.gz}"
    fi
    
    docker-compose -f docker-compose.prod.yml exec -T db \
        psql -U "${POSTGRES_USER}" "${POSTGRES_DB}" < "$backup_file"
    
    print_success "Base de datos restaurada"
}

# ============================================================================
# FUNCIONES DE MANTENIMIENTO
# ============================================================================

stop_services() {
    print_header "🛑 DETENIENDO SERVICIOS"
    
    docker-compose -f docker-compose.prod.yml down
    
    print_success "Servicios detenidos"
}

clean_all() {
    echo -e "${RED}"
    echo "⚠️  ADVERTENCIA: Esta operación eliminará:"
    echo "    - Contenedores"
    echo "    - Volúmenes (BASE DE DATOS)"
    echo "    - Redes"
    echo -e "${NC}"
    
    echo -n "¿Estás seguro? (escribe 'SI' para confirmar): "
    read confirmation
    
    if [ "$confirmation" != "SI" ]; then
        print_warning "Operación cancelada"
        return
    fi
    
    print_header "🧹 LIMPIEZA COMPLETA"
    
    docker-compose -f docker-compose.prod.yml down -v
    
    print_success "Limpieza completada"
}

validate_config() {
    print_header "✅ VALIDANDO CONFIGURACIÓN"
    
    if [ -f ./scripts/validate_deployment.sh ]; then
        ./scripts/validate_deployment.sh
    else
        print_warning "Script de validación no encontrado"
    fi
}

# ============================================================================
# MENÚ INTERACTIVO
# ============================================================================

show_menu() {
    echo ""
    print_header "🚀 FEATURE MODELS - DEPLOYMENT MANAGER"
    echo ""
    echo "  ${BLUE}BUILD:${NC}"
    echo "    1)  Construir imágenes de backend"
    echo "    2)  Construir imágenes de frontend"
    echo "    3)  Construir todas las imágenes"
    echo ""
    echo "  ${BLUE}DEPLOY:${NC}"
    echo "    4)  Desplegar servicios (Docker Compose)"
    echo "    5)  Redesplegar servicios (down + up)"
    echo "    6)  Actualizar servicios (pull + up)"
    echo "    7)  Desplegar en Docker Swarm"
    echo ""
    echo "  ${BLUE}MONITORING:${NC}"
    echo "    8)  Ver logs de todos los servicios"
    echo "    9)  Ver logs del frontend"
    echo "   10)  Ver logs del backend"
    echo "   11)  Ver estado de servicios"
    echo ""
    echo "  ${BLUE}DATABASE:${NC}"
    echo "   12)  Ejecutar migraciones"
    echo "   13)  Crear superusuario"
    echo "   14)  Backup de base de datos"
    echo "   15)  Restaurar base de datos"
    echo ""
    echo "  ${BLUE}MAINTENANCE:${NC}"
    echo "   16)  Detener servicios"
    echo "   17)  Limpiar contenedores y volúmenes"
    echo "   18)  Validar configuración"
    echo ""
    echo "    0)  Salir"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo -n "Selecciona una opción: "
}

interactive_mode() {
    print_header "🎮 MODO INTERACTIVO"
    
    while true; do
        show_menu
        read option
        
        echo ""
        
        case $option in
            1) build_backend ;;
            2) build_frontend ;;
            3) build_all ;;
            4) deploy_compose ;;
            5) redeploy ;;
            6) update_services ;;
            7) deploy_swarm ;;
            8) view_logs ;;
            9) view_logs frontend ;;
            10) view_logs feature_models_backend ;;
            11) show_status ;;
            12) run_migrations ;;
            13) create_superuser ;;
            14) backup_database ;;
            15) restore_database ;;
            16) stop_services ;;
            17) clean_all ;;
            18) validate_config ;;
            0)
                print_success "¡Hasta luego!"
                exit 0
                ;;
            *)
                print_error "Opción inválida"
                ;;
        esac
        
        echo ""
        echo -e "${YELLOW}Presiona Enter para continuar...${NC}"
        read
    done
}

# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

main() {
    # Cambiar al directorio raíz del proyecto
    cd "$(dirname "$0")/.."
    
    # Cargar variables de entorno
    load_env
    
    # Verificar modo de ejecución
    if [ "$1" == "--swarm" ]; then
        deploy_swarm
    elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        echo "Uso: $0 [OPCIÓN]"
        echo ""
        echo "Opciones:"
        echo "  (ninguna)    Modo interactivo con menú"
        echo "  --swarm      Desplegar en Docker Swarm"
        echo "  --help       Mostrar esta ayuda"
        echo ""
        exit 0
    else
        interactive_mode
    fi
}

# Ejecutar script principal
main "$@"
