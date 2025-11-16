# Configura el logging para que sea más informativo que un simple print
# --- Configuración del Logger ---
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)