from fastapi import APIRouter, status
from typing import List
from datetime import datetime
import uuid

from app.models import Task, TaskCreate
from app.database import tasks_db, get_task_or_404

router = APIRouter()


@router.get("/tasks", response_model=List[Task])
async def get_tasks():
    """Возвращает список всех задач."""
    return list(tasks_db.values())


@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Создаёт новую задачу."""
    task_id = str(uuid.uuid4())
    current_time = datetime.now()

    new_task = Task(
        id=task_id,
        created_at=current_time,
        updated_at=current_time,
        **task.model_dump()
    )

    tasks_db[task_id] = new_task
    return new_task


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Возвращает задачу по ID."""
    return get_task_or_404(task_id)


@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskCreate):
    """Полностью обновляет задачу."""
    task = get_task_or_404(task_id)
    task_data = task_update.model_dump()

    for key, value in task_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now()
    tasks_db[task_id] = task
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Удаляет задачу по ID."""
    get_task_or_404(task_id)
    del tasks_db[task_id]
    return None
