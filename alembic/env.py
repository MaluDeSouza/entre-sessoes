from logging.config import fileConfig
import os

from dotenv import load_dotenv

from alembic import context

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from database.base import Base

# Importa todos os modelos para registrá-los no metadata
from models.user import User
from models.conversation import Conversation
from models.message import Message
from models.emotional_analysis import EmotionalAnalysis
from models.emotion import Emotion
from models.keyword import Keyword
from models.insight import Insight
from pathlib import Path

load_dotenv(
    Path(__file__).parent.parent / ".env"
)

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL")
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa as migrações em modo offline."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrações em modo online."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()

else:
    run_migrations_online()