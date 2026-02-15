# =============================================================================
# バックエンド Dockerfile（マルチステージビルド）
# =============================================================================

# --- ステージ 1: ビルド ---
FROM python:3.12-slim AS builder

WORKDIR /app

# 依存パッケージのインストール（キャッシュ活用のため先にコピー）
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- ステージ 2: 本番 ---
FROM python:3.12-slim AS production

# セキュリティ: 非 root ユーザーで実行
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# ビルド済みパッケージをコピー
COPY --from=builder /install /usr/local

# アプリケーションコードをコピー
COPY src/backend/ ./

# 環境変数
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# 非 root ユーザーに切り替え
USER appuser

EXPOSE ${PORT}

# Uvicorn で起動
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
