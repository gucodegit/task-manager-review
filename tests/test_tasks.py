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
    """
    Тест частичного обновления задачи через PATCH /tasks/{task_id}.

    Проверяет контракт partial update:
    - PATCH обновляет ТОЛЬКО переданные поля, а не заменяет объект целиком (в отличие от PUT).
    - Непереданные в теле запроса поля сохраняют свои текущие значения.
    - Ответ содержит полное актуальное представление ресурса после обновления.

    Предусловия:
    - Тестовый клиент `client` инициализирован (например, fastapi.testclient.TestClient).
    - Хранилище доступно; исходная задача создаётся в рамках теста.

    Ожидаемый результат (тест пройден, если выполнены ВСЕ условия):
    1. POST /tasks успешно создаёт задачу с заданными полями.
    2. PATCH /tasks/{id} возвращает статус 200.
    3. Поле title обновлено на переданное значение.
    4. Поле priority (НЕ переданное в запросе) осталось неизменным.

    Возможные причины падения:
    - priority стал None/значением по умолчанию → эндпоинт реализован как PUT
      либо Pydantic-модель не использует exclude_unset=True / Optional-поля.
    - status_code != 200 → ошибка маршрутизации, валидации или задача не найдена.
    - title не изменился → ошибка в применении патча к модели/БД.
    - KeyError: "id" на шаге 1 → POST /tasks не возвращает id или завершился ошибкой.

    TODO (рекомендуемые дополнительные кейсы):
    - PATCH с несуществующим task_id → ожидается 404.
    - PATCH с пустым телом {} → ресурс не должен меняться.
    - PATCH с некорректным типом поля (title: 123) → ожидается 422.
    - PATCH с полем, не входящим в схему задачи → поведение должно быть явно определено.
    """    
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