"""
ヘルスチェックエンドポイント
ALB / ECS のヘルスチェックと、DB 接続状態の確認に使用。
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """ヘルスチェック（DB 接続確認込み）"""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": db_status,
    }
