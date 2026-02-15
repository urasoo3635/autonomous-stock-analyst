"""ヘルスチェックのテスト"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    """ヘルスチェックが 200 を返すこと"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root():
    """ルートエンドポイントがアプリ情報を返すこと"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Autonomous Stock Analyst"
