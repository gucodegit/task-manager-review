"""
Эталонные тесты для контрольной работы (Часть 2).
Покрывают все CRUD-эндпоинты + поле priority + негативные сценарии.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ============================================================
# GET /tasks — список задач
# ============================================================

def test_get_all_tasks_returns_list():
    """GET /tasks возвращает непустой список."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 3


def test_get_all_tasks_contains_priority():
    """У каждой задачи в списке есть поле priority."""
    response = client.get("/tasks")
    assert response.status_code == 200
    for task in response.json():
        assert "priority" in task
        assert task["priority"] in ("low", "medium", "high")


# ============================================================
# POST /tasks — создание задачи
# ============================================================

def test_create_task_success():
    """POST /tasks создаёт задачу и возвращает 201."""
    response = client.post("/tasks", json={
        "title": "Новая задача",
        "description": "Описание",
        "is_completed": False,
        "priority": "high",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Новая задача"
    assert data["priority"] == "high"
    assert "id" in data
    assert "created_at" in data


def test_create_task_default_priority_medium():
    """POST /tasks без priority → по умолчанию medium."""
    response = client.post("/tasks", json={"title": "Задача без priority"})
    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_task_empty_title_returns_422():
    """POST /tasks с пустым title → 422."""
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_create_task_long_title_returns_422():
    """POST /tasks с title > 100 символов → 422."""
    response = client.post("/tasks", json={"title": "x" * 101})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422():
    """POST /tasks с priority=urgent → 422 (не входит в enum)."""
    response = client.post("/tasks", json={
        "title": "Задача с ошибкой",
        "priority": "urgent",
    })
    assert response.status_code == 422


# ============================================================
# GET /tasks/{task_id}
# ============================================================

def test_get_task_by_id_success():
    """GET /tasks/{id} возвращает задачу по id."""
    created = client.post("/tasks", json={"title": "Для получения"}).json()
    task_id = created["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Для получения"


def test_get_task_by_id_not_found():
    """GET /tasks/{id} для несуществующего → 404."""
    response = client.get("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert "detail" in response.json()


# ============================================================
# PUT /tasks/{task_id}
# ============================================================

def test_update_task_success():
    """PUT /tasks/{id} обновляет задачу."""
    created = client.post("/tasks", json={"title": "Старое"}).json()
    task_id = created["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Новое",
        "description": "Обновлено",
        "is_completed": True,
        "priority": "high",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Новое"
    assert data["is_completed"] is True
    assert data["priority"] == "high"


def test_update_task_priority_only():
    """PUT /tasks/{id} меняет priority."""
    created = client.post("/tasks", json={"title": "Задача"}).json()
    task_id = created["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Задача",
        "priority": "low",
    })
    assert response.status_code == 200
    assert response.json()["priority"] == "low"


def test_update_task_not_found():
    """PUT /tasks/{id} для несуществующего → 404."""
    response = client.put("/tasks/nonexistent-id", json={"title": "Новое"})
    assert response.status_code == 404


# ============================================================
# DELETE /tasks/{task_id}
# ============================================================

def test_delete_task_success():
    """DELETE /tasks/{id} удаляет задачу и возвращает 204."""
    created = client.post("/tasks", json={"title": "Для удаления"}).json()
    task_id = created["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Проверяем, что задачи больше нет
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_delete_task_not_found():
    """DELETE /tasks/{id} для несуществующего → 404."""
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404


# ============================================================
# /health
# ============================================================

def test_health_check():
    """GET /health возвращает статус healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ============================================================
# Вариант 1. PATCH /tasks/{task_id} — частичное обновление
# ============================================================

def test_patch_task_partial_update():
    created = client.post("/tasks", json={"title": "Старое", "priority": "low"}).json()
    task_id = created["id"]
    
    response = client.patch(f"/tasks/{task_id}", json={"title": "Новое"})
    assert response.status_code == 200
    assert response.json()["title"] == "Новое"
    assert response.json()["priority"] == "low"  # Приоритет не изменился!

def test_patch_task_not_found():
    response = client.patch("/tasks/nonexistent", json={"title": "Новое"})
    assert response.status_code == 404


# ============================================================
# GET /tasks — список задач - начальная версия "1.Ручная разминка: напишите один тест"
# ============================================================
# from fastapi.testclient import TestClient
# from main import app

# client = TestClient(app)


# def test_get_all_tasks_returns_list():
#     """GET /tasks возвращает список (не пустой — есть 3 тестовые)."""
#     response = client.get("/tasks")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)
#     assert len(response.json()) >= 3