"""
アプリケーション設定
Pydantic Settings で環境変数を一元管理する。
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- アプリケーション ---
    app_name: str = "Autonomous Stock Analyst"
    app_version: str = "0.1.0"
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"

    # --- サーバー ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- データベース ---
    database_url: str = "postgresql://dbadmin:devpassword@localhost:5432/stock_analyst"

    # --- CORS ---
    cors_origins: list[str] = ["*"]

    # --- 外部 API ---
    fred_api_key: str | None = None

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを返す"""
    return Settings()
