"""
銘柄 API テスト
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestStockList:
    """銘柄一覧 GET /api/v1/stocks"""

    def test_list_stocks_empty(self, client: TestClient):
        """銘柄がない場合、空リストを返す"""
        with patch("api.v1.stocks.get_db") as mock_db:
            mock_session = AsyncMock()
            mock_session.execute.return_value = MagicMock(
                scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
            )
            mock_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_db.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.get("/api/v1/stocks")
            assert resp.status_code == 200
            body = resp.json()
            assert "stocks" in body
            assert "total" in body


class TestHealthCheck:
    """ヘルスチェック"""

    def test_health(self, client: TestClient):
        """ヘルスチェックが 200 を返す"""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_root(self, client: TestClient):
        """ルートエンドポイントが 200 を返す"""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "api" in resp.json()


class TestSecurityHeaders:
    """セキュリティヘッダーの確認"""

    def test_security_headers_present(self, client: TestClient):
        """セキュリティヘッダーが付与されていることを確認"""
        resp = client.get("/health")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("X-Frame-Options") == "DENY"
        assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
