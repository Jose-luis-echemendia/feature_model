"""
Script para poblar la base de datos con datos de prueba (Database Seeding)

DEPRECADO: Este archivo se mantiene por compatibilidad pero ahora
simplemente importa y ejecuta el módulo centralizado en app.seed

Uso:
    python -m app.seed_data

Nuevo uso recomendado:
    python -m app.seed.main
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar el sistema centralizado de seeding
from app.seed.main import seed_all


def main():
    """Función principal - redirige al sistema centralizado"""

    # Ejecutar el seeding centralizado
    seed_all()


if __name__ == "__main__":
    main()
