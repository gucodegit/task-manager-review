# ---- Этап сборки ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Устанавливаем зависимости в отдельную директорию для кэширования
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---- Финальный этап ----
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /root/.local

# Копируем исходный код
COPY . .

# Добавляем локальные пакеты в PATH
ENV PATH=/root/.local/bin:$PATH

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]