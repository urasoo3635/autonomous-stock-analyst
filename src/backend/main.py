"""
Autonomous Stock Analyst - バックエンド API
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from api.router import router as api_router
from core.config import get_settings
from core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)

# rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


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


# 本番環境では docs を無効化
_docs_url = None if settings.is_production else "/docs"
_redoc_url = None if settings.is_production else "/redoc"

app = FastAPI(
    title=settings.app_name,
    description="株式分析・予測 API",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
)

# --- ミドルウェア ---

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# Trusted Host（本番環境のみ）
if settings.is_production and settings.allowed_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """セキュリティヘッダーを付与するミドルウェア"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        )
    return response


# ルーター登録
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """グローバル例外ハンドラー（内部エラーの詳細を外部に漏らさない）"""
    logger.error("未処理の例外: %s %s - %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "内部サーバーエラーが発生しました"},
    )


@app.get("/health", include_in_schema=False)
async def health_check() -> dict:
    """簡易ヘルスチェック（ALB 用、DB 依存なし）"""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
async def root() -> dict:
    """ルートエンドポイント"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if not settings.is_production else None,
        "api": "/api/v1",
    }
