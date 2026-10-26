from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime


class Priority(str, Enum):
    """Допустимые значения приоритета задачи."""
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    """Базовая модель задачи."""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False
    priority: Priority = Priority.medium


class TaskCreate(TaskBase):
    """Модель для создания задачи."""
    pass


class Task(TaskBase):
    """Модель ответа с системными полями."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    