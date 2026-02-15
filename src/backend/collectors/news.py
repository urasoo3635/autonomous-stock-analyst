"""
ニュース取得モジュール
RSS フィードからニュースを逐次取得する（DB 保存なし）。
"""
import logging
from datetime import datetime

import feedparser
import httpx

logger = logging.getLogger(__name__)

# Google News RSS（日本語版）
GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"


async def fetch_news(query: str, max_items: int = 10) -> list[dict]:
    """
    ニュースを逐次取得する（DB 保存なし）。

    Args:
        query: 検索キーワード（銘柄名 or ティッカー）
        max_items: 最大取得件数

    Returns:
        list[dict]: ニュース記事のリスト
    """
    logger.info("ニュース取得開始: query=%s", query)

    url = GOOGLE_NEWS_RSS_URL.format(query=query)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()

    feed = feedparser.parse(response.text)

    articles = []
    for entry in feed.entries[:max_items]:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6]).isoformat()

        articles.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source": entry.get("source", {}).get("title", ""),
            "published_at": published,
            "summary": entry.get("summary", ""),
        })

    logger.info("ニュース取得完了: query=%s, %d件", query, len(articles))
    return articles
