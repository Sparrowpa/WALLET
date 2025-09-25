import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# Stupid path!!! I dont now how to fix!!!

from sqlalchemy import create_engine, pool
from alembic import context
from app.config import DATABASE_URL_ALEMBIC
from app.models import Base

# Model
target_metadata = Base.metadata

# Sync engine!!!
connectable = create_engine(DATABASE_URL_ALEMBIC, poolclass=pool.NullPool)

# Setup Alembic and run migrations
with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
