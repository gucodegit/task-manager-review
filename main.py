from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Импортируем роутер
from app.routers import tasks

app = FastAPI(title="Task Manager API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер (все эндпоинты из tasks.py)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Task Manager API",
        "docs": "/docs",
        "tasks_endpoint": "/tasks"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Для учебного проекта и для работы в Docker `0.0.0.0` оставляем, 
    # чтобы bandit не возвращал код ошибки 1
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104

