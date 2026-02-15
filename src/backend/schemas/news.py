"""
ニュース関連スキーマ
"""
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """ニュース記事"""

    title: str
    url: str
    source: str
    published_at: str | None
    summary: str


class NewsResponse(BaseModel):
    """ニュース取得レスポンス"""

    query: str
    articles: list[NewsArticle]
    total: int
