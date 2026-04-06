"""Endpoints para consultar estado/resultados de tareas Celery."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_verified_user
from app.core.celery import celery_app


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(get_verified_user)],
)


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="Estado y resultado de tarea",
    description="Devuelve el estado y el resultado (si existe) de una tarea Celery.",
)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    async_result = celery_app.AsyncResult(task_id)
    if async_result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    response = TaskStatusResponse(task_id=task_id, status=async_result.status)
    if async_result.successful():
        response.result = async_result.result
    elif async_result.failed():
        response.error = str(async_result.result)

    return response
