"""
Autonomous Stock Analyst - バックエンド API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Autonomous Stock Analyst API",
    description="株式分析・予測 API",
    version="0.1.0",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント（ALB / ECS 用）"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "app": "Autonomous Stock Analyst",
        "version": "0.1.0",
        "docs": "/docs",
    }
