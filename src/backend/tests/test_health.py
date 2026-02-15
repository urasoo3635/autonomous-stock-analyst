"""ヘルスチェックのテスト"""


def test_health_check(client):
    """簡易ヘルスチェックが 200 を返すこと"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root(client):
    """ルートエンドポイントがアプリ情報を返すこと"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Autonomous Stock Analyst"
    assert "docs" in data
    assert "api" in data
