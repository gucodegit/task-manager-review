import uuid
from datetime import datetime
from fastapi import HTTPException, status
from app.models import Task

# In-memory база данных
tasks_db = {}

initial_data = [
    {"title": "Изучить FastAPI", "description": "Прочитать документацию и сделать CRUD",
     "is_completed": False, "priority": "high"},
    {"title": "Реализовать CRUD", "description": "Написать код для каждого эндпоинта",
     "is_completed": False, "priority": "medium"},
    {"title": "Написать тесты", "description": "Покрыть pytest все эндпоинты",
     "is_completed": False, "priority": "low"},
]

# Инициализация задач
for data in initial_data:
    task_id = str(uuid.uuid4())
    current_time = datetime.now()
    new_task = Task(
        id=task_id,
        created_at=current_time,
        updated_at=current_time,
        **data
    )
    tasks_db[task_id] = new_task


def get_task_or_404(task_id: str) -> Task:
    """Возвращает задачу или выбрасывает 404."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return tasks_db[task_id]
