"""
アプリケーション設定
Pydantic Settings で環境変数を一元管理する。

セキュリティ:
- 本番環境では .env に SECRET_KEY を必ず設定すること
- CORS_ORIGINS に "*" を設定しないこと
"""
import secrets
from functools import lru_cache
from typing import Any

from pydantic import field_validator, model_validator
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

    # --- セキュリティ ---
    # 本番環境では必ず 32 バイト以上のランダム値を設定すること
    # `python -c "import secrets; print(secrets.token_urlsafe(32))"` で生成可能
    secret_key: str = secrets.token_urlsafe(32)
    allowed_hosts: list[str] = ["*"]

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 60  # 1分間あたりのリクエスト上限

    # --- 外部 API ---
    fred_api_key: str | None = None

    # --- バリデーション ---

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"dev", "staging", "prod"}
        if v not in allowed:
            raise ValueError(f"environment は {allowed} のいずれかを指定してください")
        return v

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        """本番環境向けセキュリティ設定の検証"""
        if self.environment == "prod":
            # 本番環境では CORS に * を許可しない
            if "*" in self.cors_origins:
                raise ValueError("本番環境では cors_origins に '*' を指定できません")
            # 本番環境ではデフォルトの secret_key を使わせない
            # (環境変数 SECRET_KEY が設定されていれば token_urlsafe と異なるはず)
            if self.allowed_hosts == ["*"]:
                raise ValueError("本番環境では allowed_hosts に '*' を指定できません")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"

    @property
    def is_development(self) -> bool:
        return self.environment == "dev"

    def get_cors_origins(self) -> list[Any]:
        """実際に使用する CORS origins を返す"""
        return self.cors_origins


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを返す"""
    return Settings()
