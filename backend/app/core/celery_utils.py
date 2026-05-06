from typing import Any, Iterable

from app.core.celery import celery_app
from app.core.logging import get_logger

log = get_logger(__name__)

# Priority mapping: high -> validation queue, medium -> default, low -> maintenance
PRIORITY_QUEUE_MAP = {
    "high": "validation",
    "medium": "default",
    "low": "maintenance",
}


def enqueue_task(task_name: str, args: Iterable[Any] | None = None, kwargs: dict | None = None, *, priority: str = "medium", delay: int | None = None):
    """
    Enqueue a Celery task using a logical priority that maps to pre-defined queues.

    Args:
        task_name: Full task name (e.g. "app.tasks.feature_model_analysis.run_feature_model_analysis")
        args: Positional args
        kwargs: Keyword args
        priority: One of 'high', 'medium', 'low'
        delay: Optional countdown in seconds

    Returns:
        AsyncResult or result of apply_async
    """
    q = PRIORITY_QUEUE_MAP.get(priority, "default")
    try:
        options = {"queue": q, "routing_key": q}
        if delay:
            result = celery_app.send_task(task_name, args=args or [], kwargs=kwargs or {}, countdown=delay, **options)
        else:
            result = celery_app.send_task(task_name, args=args or [], kwargs=kwargs or {}, **options)
        log.info("celery.task.enqueued", task=task_name, queue=q, priority=priority)
        return result
    except Exception as e:
        log.error("celery.enqueue_failed", task=task_name, error=str(e))
        raise
