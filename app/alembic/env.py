import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#Долбаный костыль с путями приследует меня

from sqlalchemy import create_engine, pool
from alembic import context
from app.config import DATABASE_URL_ALEMBIC
from app.models import Base

# Метаданные моделей
target_metadata = Base.metadata

# синхронный движок для Alembic
connectable = create_engine(DATABASE_URL_ALEMBIC, poolclass=pool.NullPool)

# Конфигурируем Alembic и запускаем миграции
with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()