
from celery import Celery
from app.core.config import settings

# 1. Define la URL del broker y del backend de resultados usando Redis
#    El nombre 'redis' corresponde al nombre del servicio en docker-compose.yml
redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# 2. Crea la instancia de la aplicación Celery
celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url
)

# 3. Importa la tarea que definiremos a continuación
celery_app.autodiscover_tasks(["app.tasks"])