"""
ロギング設定
構造化ログを提供する。
"""
import logging
import sys

from core.config import get_settings


def setup_logging() -> None:
    """アプリケーション全体のロギングを設定する"""
    settings = get_settings()

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # 外部ライブラリのログレベルを調整
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """モジュール用のロガーを取得する"""
    return logging.getLogger(name)
