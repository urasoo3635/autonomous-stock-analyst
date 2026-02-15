"""
API ルーター集約
全 v1 エンドポイントをまとめる。
"""
from fastapi import APIRouter

from api.v1 import health, macro, news, stocks

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, tags=["ヘルスチェック"])
router.include_router(stocks.router, tags=["銘柄"])
router.include_router(news.router, tags=["ニュース"])
router.include_router(macro.router, tags=["マクロ経済指標"])
