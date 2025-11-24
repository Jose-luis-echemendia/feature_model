#!/bin/bash

# Script de ayuda para comandos de despliegue
# Proporciona comandos útiles para gestionar el despliegue en producción

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar el menú
show_menu() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  🚀 COMANDOS DE DESPLIEGUE - Feature Models"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "  ${BLUE}BUILD:${NC}"
    echo "    1) Construir imágenes de backend"
    echo "    2) Construir imágenes de frontend"
    echo "    3) Construir todas las imágenes"
    echo ""
    echo "  ${BLUE}DEPLOY:${NC}"
    echo "    4) Desplegar servicios"
    echo "    5) Redesplegar servicios (down + up)"
    echo "    6) Actualizar servicios (pull + up)"
    echo ""
    echo "  ${BLUE}MANAGE:${NC}"
    echo "    7) Ver logs de todos los servicios"
    echo "    8) Ver logs del frontend"
    echo "    9) Ver logs del backend"
    echo "   10) Ver estado de servicios"
    echo ""
    echo "  ${BLUE}DATABASE:${NC}"
    echo "   11) Ejecutar migraciones"
    echo "   12) Crear superusuario"
    echo "   13) Backup de base de datos"
    echo ""
    echo "  ${BLUE}MAINTENANCE:${NC}"
    echo "   14) Detener servicios"
    echo "   15) Limpiar contenedores y volúmenes"
    echo "   16) Validar configuración"
    echo ""
    echo "    0) Salir"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo -n "Selecciona una opción: "
}

# Función para construir backend
build_backend() {
    echo -e "${GREEN}📦 Construyendo imagen del backend...${NC}"
    docker build -t ${DOCKER_IMAGE_BACKEND}:${TAG:-latest} ./backend
    echo -e "${GREEN}✅ Backend construido${NC}"
}

# Función para construir frontend
build_frontend() {
    echo -e "${GREEN}📦 Construyendo imagen del frontend...${NC}"
    docker build -t ${DOCKER_IMAGE_FRONTEND}:${TAG:-latest} \
        --build-arg VITE_API_URL=https://api.${DOMAIN} \
        --build-arg NODE_ENV=production \
        ./frontend
    echo -e "${GREEN}✅ Frontend construido${NC}"
}

# Función para desplegar
deploy() {
    echo -e "${GREEN}🚀 Desplegando servicios...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    echo -e "${GREEN}✅ Servicios desplegados${NC}"
}

# Función para ver logs
view_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose -f docker-compose.prod.yml logs -f $service
    fi
}

# Función para ver estado
status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose -f docker-compose.prod.yml ps
}

# Función para migraciones
run_migrations() {
    echo -e "${GREEN}🔄 Ejecutando migraciones...${NC}"
    docker-compose -f docker-compose.prod.yml exec feature_models_backend alembic upgrade head
    echo -e "${GREEN}✅ Migraciones completadas${NC}"
}

# Función para crear superusuario
create_superuser() {
    echo -e "${GREEN}👤 Creando superusuario...${NC}"
    docker-compose -f docker-compose.prod.yml exec feature_models_backend python -m app.initial_data
    echo -e "${GREEN}✅ Superusuario creado${NC}"
}

# Función para backup
backup_db() {
    echo -e "${GREEN}💾 Creando backup de la base de datos...${NC}"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_${TIMESTAMP}.sql
    echo -e "${GREEN}✅ Backup creado: backup_${TIMESTAMP}.sql${NC}"
}

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    exit 1
fi

# Loop principal
while true; do
    show_menu
    read option
    
    case $option in
        1)
            build_backend
            ;;
        2)
            build_frontend
            ;;
        3)
            build_backend
            build_frontend
            ;;
        4)
            deploy
            ;;
        5)
            echo -e "${YELLOW}🔄 Redespliegando servicios...${NC}"
            docker-compose -f docker-compose.prod.yml down
            deploy
            ;;
        6)
            echo -e "${YELLOW}🔄 Actualizando servicios...${NC}"
            docker-compose -f docker-compose.prod.yml pull
            deploy
            ;;
        7)
            view_logs
            ;;
        8)
            view_logs frontend
            ;;
        9)
            view_logs feature_models_backend
            ;;
        10)
            status
            ;;
        11)
            run_migrations
            ;;
        12)
            create_superuser
            ;;
        13)
            backup_db
            ;;
        14)
            echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
            docker-compose -f docker-compose.prod.yml down
            echo -e "${GREEN}✅ Servicios detenidos${NC}"
            ;;
        15)
            echo -e "${RED}⚠️  ¿Estás seguro? Esto eliminará contenedores y volúmenes (s/n): ${NC}"
            read confirm
            if [ "$confirm" = "s" ]; then
                docker-compose -f docker-compose.prod.yml down -v
                echo -e "${GREEN}✅ Limpieza completada${NC}"
            fi
            ;;
        16)
            ./validate_deployment.sh
            ;;
        0)
            echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opción inválida${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}Presiona Enter para continuar...${NC}"
    read
done
