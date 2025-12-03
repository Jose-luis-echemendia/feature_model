#!/usr/bin/env python3
"""
Script para sincronizar documentación de docs/ a internal_docs/docs/
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
SOURCE = PROJECT_ROOT / "docs"
TARGET = PROJECT_ROOT / "internal_docs" / "docs"

logger.info("=" * 60)
logger.info("📚 Iniciando sincronización de documentación")
logger.info("=" * 60)
logger.info(f"📅 Timestamp: {datetime.now().isoformat()}")
logger.info(f"🏠 Raíz del proyecto: {PROJECT_ROOT.absolute()}")
logger.info(f"📂 Carpeta origen: {SOURCE.absolute()}")
logger.info(f"📂 Carpeta destino: {TARGET.absolute()}")
logger.info("")

# Verificar que la carpeta fuente existe
logger.info("🔍 Verificando existencia de carpeta origen...")
if not SOURCE.exists():
    logger.warning(f"⚠️ La carpeta '{SOURCE}' no existe")
    logger.info("ℹ️ La carpeta docs/ no se encuentra en el contenedor.")
    logger.info("ℹ️ Esto es normal si no se ha configurado la documentación aún.")
    logger.info(
        "ℹ️ Para habilitar docs, asegúrate de copiar la carpeta en el Dockerfile."
    )
    print("⚠️ La carpeta docs/ no existe. Sincronización omitida.")
    logger.info("=" * 60)
    logger.info("⏭️ Sincronización omitida - carpeta origen no encontrada")
    logger.info("=" * 60)
    exit(0)  # Exit 0 para no fallar el prestart.sh

logger.info(f"✅ Carpeta origen encontrada: {SOURCE}")
logger.debug(f"Ruta absoluta: {SOURCE.absolute()}")

# Contar archivos en origen
source_files = list(SOURCE.glob("*.md"))
logger.info(f"📊 Archivos .md encontrados en origen: {len(source_files)}")
for f in source_files:
    logger.debug(f"  - {f.name} ({f.stat().st_size} bytes)")

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

# Copia los archivos
logger.info("📋 Copiando archivos de origen a destino...")
copied_count = 0
failed_count = 0

for file in source_files:
    try:
        destination = TARGET / file.name
        logger.debug(f"  📄 Copiando: {file.name}")
        shutil.copy(file, destination)
        logger.debug(f"    ✓ Destino: {destination}")
        copied_count += 1
    except Exception as e:
        logger.error(f"  ❌ Error copiando {file.name}: {e}")
        failed_count += 1

logger.info("")
logger.info("=" * 60)
logger.info("📊 Resumen de sincronización:")
logger.info(f"  ✅ Archivos copiados: {copied_count}")
logger.info(f"  ❌ Archivos fallidos: {failed_count}")
logger.info(f"  🗑️ Archivos eliminados: {deleted_count}")
logger.info("=" * 60)

if failed_count > 0:
    logger.error("💥 Sincronización completada con errores")
    print(f"Documentación sincronizada con {failed_count} errores.")
    exit(1)
else:
    logger.info("✅ Sincronización completada exitosamente")
    print("Documentación sincronizada.")
    exit(0)
