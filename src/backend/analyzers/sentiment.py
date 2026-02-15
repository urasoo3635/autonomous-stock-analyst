"""
センチメント分析モジュール
ニュース記事のテキストから感情スコア（Positive/Negative/Neutral）を算出する。
"""
import logging

# transformers はサイズが大きいため、インポート時にエラーハンドリングするか、遅延ロードする
try:
    from transformers import pipeline
except ImportError:
    pipeline = None

logger = logging.getLogger(__name__)

# 金融特化のセンチメント分析モデル
MODEL_NAME = "ProsusAI/finbert"


class SentimentAnalyzer:
    """センチメント分析クラス"""

    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        """パイプラインのシングルトン取得（初回ロード時にモデルをダウンロードするため時間がかかる）"""
        if cls._pipeline is None:
            if pipeline is None:
                raise ImportError("transformers ライブラリがインストールされていません")
            logger.info("センチメント分析モデルのロード開始: %s", MODEL_NAME)
            cls._pipeline = pipeline("sentiment-analysis", model=MODEL_NAME)
            logger.info("センチメント分析モデルのロード完了")
        return cls._pipeline

    @classmethod
    def analyze(cls, text: str) -> dict:
        """
        テキストのセンチメントを分析する。

        Returns:
            dict: {label: "positive"|"negative"|"neutral", score: float}
        """
        if not text:
            return {"label": "neutral", "score": 0.0}

        pipe = cls.get_pipeline()
        # テキストが長すぎる場合は切り詰める（BERTの制限）
        truncated_text = text[:512]
        result = pipe(truncated_text)[0]
        return {"label": result["label"], "score": result["score"]}
