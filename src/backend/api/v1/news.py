"""
ニュース取得エンドポイント（逐次取得、DB 保存なし）
"""
from fastapi import APIRouter, HTTPException

from collectors.news import fetch_news
from schemas.news import NewsResponse

router = APIRouter(prefix="/news")


@router.get("/{query}", response_model=NewsResponse)
async def get_news(
    query: str,
    max_items: int = 10,
) -> dict:
    """ニュースを取得する（逐次、DB 保存なし）"""
    try:
        articles = await fetch_news(query, max_items=max_items)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"ニュースの取得に失敗しました: {e}",
        )

    return {
        "query": query,
        "articles": articles,
        "total": len(articles),
    }
