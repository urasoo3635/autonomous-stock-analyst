"""
テスト共通設定
"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    """テスト用 HTTP クライアント"""
    return TestClient(app)
