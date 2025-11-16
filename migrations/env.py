from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

import app.db.models  # noqa: F401
from app.core.config import settings
from app.db.postgres import Base

config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Беремо async URL з settings і конвертуємо в sync
async_url = settings.postgres_url
sync_url = async_url.replace("+asyncpg", "")

# Підставляємо в конфіг Alembic
config.set_main_option("sqlalchemy.url", sync_url)

# Вся метадані моделей для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
