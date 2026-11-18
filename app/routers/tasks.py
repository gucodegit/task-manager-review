# app/routers/tasks.py
from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models import Task, TaskCreate, TaskPatch
from app.database import DBTask, get_db

router = APIRouter()

@router.get("/tasks", response_model=List[Task])
def get_tasks(db: Session = Depends(get_db)):
    """Возвращает список всех задач из базы данных."""
    # Запрашиваем все задачи из таблицы
    tasks = db.query(DBTask).all()
    return tasks


@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Создаёт новую задачу в базе данных."""
    task_id = str(uuid.uuid4())
    current_time = datetime.now()

    # Создаем объект ORM-модели
    new_task = DBTask(
        id=task_id,
        created_at=current_time,
        updated_at=current_time,
        **task.model_dump()
    )

    # Сохраняем в БД
    db.add(new_task)
    db.commit()
    db.refresh(new_task) # Обновляем объект, чтобы получить данные из БД
    
    return new_task


@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Возвращает задачу по ID."""
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskCreate, db: Session = Depends(get_db)):
    """Полностью обновляет задачу."""
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump()

    # Обновляем поля
    for key, value in task_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now()
    
    # Сохраняем изменения
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Удаляет задачу по ID."""
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(task)
    db.commit()
    return None


@router.patch("/tasks/{task_id}", response_model=Task)
def patch_task(task_id: str, task_update: TaskPatch, db: Session = Depends(get_db)):
    """Частично обновляет задачу (только переданные поля)."""
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # exclude_unset=True берет только те поля, которые прислал клиент
    update_data = task_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(task, key, value)
        
    task.updated_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    return task
