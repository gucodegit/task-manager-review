# seed.py
from app.database import SessionLocal, engine, Base, DBTask
from datetime import datetime
import uuid

def seed_data():
    # На всякий случай создаем таблицы (если их вдруг нет)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # ВАЖНО: Проверяем, есть ли уже задачи, чтобы не создавать дубликаты
        if db.query(DBTask).first():
            print("База данных уже содержит задачи. Пропускаем инициализацию.")
            return

        initial_data = [
            {"title": "Изучить FastAPI", "description": "Прочитать документацию", "is_completed": False, "priority": "medium"},
            {"title": "Реализовать CRUD", "description": "Написать код", "is_completed": False, "priority": "high"},
            {"title": "Написать тесты", "description": "Покрыть pytest", "is_completed": False, "priority": "low"},
        ]

        for data in initial_data:
            current_time = datetime.now()
            new_task = DBTask(
                id=str(uuid.uuid4()),
                created_at=current_time,
                updated_at=current_time,
                **data
            )
            db.add(new_task)

        db.commit()
        print("✅ База данных успешно инициализирована 3 задачами!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
