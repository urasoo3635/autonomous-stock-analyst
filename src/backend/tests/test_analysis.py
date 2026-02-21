"""
分析 API テスト
"""
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestSentimentAnalysis:
    """センチメント分析 POST /api/v1/analysis/sentiment"""

    def test_sentiment_positive(self, client: TestClient):
        """ポジティブなテキストで sentiment エンドポイントが正常に動作する"""
        with patch("analyzers.sentiment.SentimentAnalyzer.analyze") as mock_analyze:
            mock_analyze.return_value = {"label": "positive", "score": 0.95}
            resp = client.post(
                "/api/v1/analysis/sentiment",
                json={"text": "Strong earnings beat expectations!"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["label"] == "positive"
            assert 0 <= body["score"] <= 1

    def test_sentiment_text_too_long(self, client: TestClient):
        """1000 文字超のテキストはバリデーションエラーになる"""
        resp = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "x" * 1001},
        )
        assert resp.status_code == 422


class TestTechnicalIndicators:
    """テクニカル指標 GET /api/v1/analysis/{ticker}/technical"""

    def test_technical_no_data(self, client: TestClient):
        """データがない場合は 404 または空リストを返す"""
        with patch("api.v1.analysis.calculate_technical_indicators") as mock_calc:
            mock_calc.side_effect = ValueError("データが見つかりません")
            resp = client.get("/api/v1/analysis/INVALID/technical")
            assert resp.status_code == 404

    def test_technical_returns_list(self, client: TestClient):
        """正常なデータがある場合はリストを返す"""
        dummy_df = pd.DataFrame(
            {
                "open": [100.0],
                "high": [105.0],
                "low": [99.0],
                "close": [103.0],
                "volume": [100000.0],
                "SMA_20": [101.0],
                "SMA_50": [100.0],
                "SMA_200": [None],
                "RSI_14": [55.0],
                "MACD_12_26_9": [1.2],
                "MACDh_12_26_9": [0.3],
                "MACDs_12_26_9": [0.9],
                "BBU_20_2.0": [110.0],
                "BBM_20_2.0": [103.0],
                "BBL_20_2.0": [96.0],
            },
            index=pd.to_datetime(["2025-01-01"]),
        )
        dummy_db = AsyncMock()
        with patch("api.v1.analysis.calculate_technical_indicators") as mock_calc, \
             patch("api.v1.analysis.get_db") as mock_db:
            mock_calc.return_value = dummy_df
            mock_db.return_value.__aenter__ = AsyncMock(return_value=dummy_db)
            mock_db.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = client.get("/api/v1/analysis/7203.T/technical?days=1")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)
