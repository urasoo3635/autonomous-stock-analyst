"""
Alembic 環境設定
DB URL は環境変数 DATABASE_URL から取得する。
"""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config オブジェクト
config = context.config

# ロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 環境変数からDB URLを上書き（Dockerや本番環境で使用）
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # asyncpg → psycopg2 用 URL に変換（Alembic は同期接続を使用）
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://").replace(
        "postgresql://", "postgresql://"
    )
    config.set_main_option("sqlalchemy.url", sync_url)

# target_metadata: モデルのメタデータを自動マイグレーションに使用
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base  # noqa: E402
import models.stock  # noqa: F401, E402
import models.macro  # noqa: F401, E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """オフラインモードでマイグレーション実行"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """オンラインモードでマイグレーション実行"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
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
