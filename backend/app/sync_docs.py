#!/usr/bin/env python3
"""
Script para sincronizar documentación de 3 fuentes a internal_docs/docs/
- Root docs (docs/ del proyecto)
- Backend docs (backend/docs/)
- Frontend docs (frontend/docs/)
"""
import shutil
import logging
import sys
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Obtener el directorio raíz del proyecto (un nivel arriba de app/)
PROJECT_ROOT = Path(__file__).parent.parent
TARGET = PROJECT_ROOT / "internal_docs" / "docs"

# Definir las 3 fuentes de documentación
SOURCES = {
    "root": PROJECT_ROOT / "root_docs",      # docs/ del root del proyecto
    "backend": PROJECT_ROOT / "backend_docs", # backend/docs/
    "frontend": PROJECT_ROOT / "frontend_docs" # frontend/docs/
}

logger.info("=" * 80)
logger.info("📚 Iniciando sincronización de documentación desde 3 fuentes")
logger.info("=" * 80)
logger.info(f"📅 Timestamp: {datetime.now().isoformat()}")
logger.info(f"🏠 Raíz del proyecto: {PROJECT_ROOT.absolute()}")
logger.info(f"📂 Carpeta destino: {TARGET.absolute()}")
logger.info("")
logger.info("📂 Carpetas origen:")
for name, path in SOURCES.items():
    logger.info(f"  - {name.upper()}: {path.absolute()}")
logger.info("")

# Verificar/crear carpeta destino
logger.info("🔍 Verificando carpeta destino...")
if not TARGET.exists():
    logger.warning(f"⚠️ Carpeta destino no existe, creándola: {TARGET}")
    TARGET.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Carpeta destino creada")
else:
    logger.info(f"✅ Carpeta destino encontrada: {TARGET}")

# Limpia docs internos
logger.info("🧹 Limpiando archivos existentes en destino...")
deleted_count = 0
for f in TARGET.glob("*"):
    if f.is_file():
        logger.debug(f"  🗑️ Eliminando: {f.name}")
        f.unlink()
        deleted_count += 1

logger.info(f"✅ Archivos eliminados: {deleted_count}")
logger.info("")

# Estadísticas globales
total_copied = 0
total_failed = 0
total_found = 0

# Procesar cada fuente de documentación
for source_name, source_path in SOURCES.items():
    logger.info("=" * 80)
    logger.info(f"� Procesando fuente: {source_name.upper()}")
    logger.info("=" * 80)
    logger.info(f"📂 Ruta: {source_path}")
    
    # Verificar que la carpeta fuente existe
    if not source_path.exists():
        logger.warning(f"⚠️ La carpeta '{source_path}' no existe")
        logger.info(f"ℹ️ La carpeta {source_name}_docs/ no se encuentra en el contenedor.")
        logger.info(f"ℹ️ Esto es normal si no se ha configurado documentación de {source_name} aún.")
        logger.info("")
        continue
    
    logger.info(f"✅ Carpeta fuente encontrada: {source_path}")
    
    # Buscar archivos markdown
    source_files = list(source_path.glob("**/*.md"))  # Recursivo
    logger.info(f"📊 Archivos .md encontrados: {len(source_files)}")
    total_found += len(source_files)
    
    if len(source_files) == 0:
        logger.warning(f"⚠️ No se encontraron archivos .md en {source_name}_docs/")
        logger.info("")
        continue
    
    # Mostrar archivos encontrados
    for f in source_files:
        rel_path = f.relative_to(source_path)
        logger.debug(f"  - {rel_path} ({f.stat().st_size} bytes)")
    
    # Copiar archivos con prefijo para evitar colisiones
    logger.info(f"📋 Copiando archivos de {source_name}...")
    copied_count = 0
    failed_count = 0
    
    for file in source_files:
        try:
            # Obtener ruta relativa para mantener estructura de carpetas
            rel_path = file.relative_to(source_path)
            
            # Crear nombre de archivo con prefijo para evitar colisiones
            # Ejemplo: index.md -> root_index.md
            #          api/endpoints.md -> backend_api_endpoints.md
            if rel_path.parent != Path('.'):
                # Si está en subcarpeta, incluir el path en el nombre
                new_name = f"{source_name}_{rel_path.parent}_{rel_path.name}".replace('/', '_').replace('\\', '_')
            else:
                new_name = f"{source_name}_{rel_path.name}"
            
            destination = TARGET / new_name
            
            logger.debug(f"  📄 {rel_path} -> {new_name}")
            shutil.copy(file, destination)
            copied_count += 1
            total_copied += 1
            
        except Exception as e:
            logger.error(f"  ❌ Error copiando {file.name}: {e}")
            failed_count += 1
            total_failed += 1
    
    logger.info(f"✅ Archivos copiados de {source_name}: {copied_count}")
    if failed_count > 0:
        logger.error(f"❌ Archivos fallidos de {source_name}: {failed_count}")
    logger.info("")

# Resumen final
logger.info("=" * 80)
logger.info("📊 RESUMEN FINAL DE SINCRONIZACIÓN")
logger.info("=" * 80)
logger.info(f"  📁 Fuentes procesadas: {len(SOURCES)}")
logger.info(f"  📄 Archivos encontrados: {total_found}")
logger.info(f"  ✅ Archivos copiados: {total_copied}")
logger.info(f"  ❌ Archivos fallidos: {total_failed}")
logger.info(f"  🗑️ Archivos eliminados previamente: {deleted_count}")
logger.info("=" * 80)

# Listar archivos finales en destino
final_files = list(TARGET.glob("*.md"))
logger.info(f"📂 Archivos finales en {TARGET}:")
for f in sorted(final_files):
    logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")

logger.info("")

# Crear index.md desde root_index.md para MkDocs
root_index = TARGET / "root_index.md"
index_md = TARGET / "index.md"
if root_index.exists():
    logger.info("📄 Creando index.md desde root_index.md...")
    try:
        import shutil
        shutil.copy2(root_index, index_md)
        logger.info(f"✅ index.md creado exitosamente ({index_md.stat().st_size} bytes)")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo crear index.md: {e}")
else:
    logger.warning("⚠️ root_index.md no encontrado, index.md no se creará")

logger.info("")

if total_failed > 0:
    logger.error("💥 Sincronización completada con errores")
    print(f"Documentación sincronizada con {total_failed} errores de {total_found} archivos.")
    exit(1)
elif total_copied == 0:
    logger.warning("⚠️ No se copiaron archivos (carpetas origen vacías o no existen)")
    print("Advertencia: No se encontraron archivos de documentación para sincronizar.")
    exit(0)
else:
    logger.info("✅ Sincronización completada exitosamente")
    print(f"Documentación sincronizada: {total_copied} archivos de 3 fuentes.")
    exit(0)
