"""
Autonomous Stock Analyst - バックエンド API
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import router as api_router
from core.config import get_settings
from core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理"""
    setup_logging()
    logger.info(
        "アプリケーション起動: env=%s, version=%s",
        settings.environment,
        settings.app_version,
    )
    yield
    logger.info("アプリケーション終了")


app = FastAPI(
    title=settings.app_name,
    description="株式分析・予測 API",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """グローバル例外ハンドラー"""
    logger.error("未処理の例外: %s %s - %s", request.method, request.url, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部サーバーエラーが発生しました"},
    )


@app.get("/health")
async def health_check() -> dict:
    """簡易ヘルスチェック（ALB 用、DB 依存なし）"""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
async def root() -> dict:
    """ルートエンドポイント"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api": "/api/v1",
    }
