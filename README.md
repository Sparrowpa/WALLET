Wallet REST API — тестовое задание

Описание:
REST API для управления балансами кошельков.
Реализованы операции пополнения и снятия средств, с учётом конкурентной обработки параллельных запросов.

1️⃣ Установка зависимостей

Стек технологий:
<pre>
|FastAPI
|PostgreSQL
|SQLAlchemy (асинхронно)
|Alembic (миграции)
|Docker / Docker Compose
|pytest (тесты)

Python 3.13.2

python -m venv .venv
# Windows

.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt
Основа с актуальными версиями для сборки проекта:

22.09.2025

fastapi==0.117.1
uvicorn==0.36.0
SQLAlchemy==2.0.43
asyncpg==0.30.0
alembic==1.16.5
pydantic==2.11.9
pytest==8.4.2
pytest-asyncio==1.2.0
psycopg2==2.9.10
</pre>
2️⃣ Установка Docker и Docker Compose
Приложение работает, теперь узнать бы работает ли оно правильно...