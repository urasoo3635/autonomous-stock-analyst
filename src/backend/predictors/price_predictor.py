"""
株価予測エンジン
LightGBM を使用して将来の株価変動を予測する。
"""
import logging
from datetime import date, timedelta

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class PricePredictor:
    """株価予測クラス"""

    def __init__(self):
        self.model = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル指標を含む DataFrame から特徴量を作成する。
        （移動平均乖離率、RSI、MACD、ボリンジャーバンド位置など）
        """
        features = pd.DataFrame(index=df.index)

        # 1. 移動平均乖離率
        if "SMA_20" in df.columns:
            features["deviate_20"] = (df["close"] - df["SMA_20"]) / df["SMA_20"]
        if "SMA_50" in df.columns:
            features["deviate_50"] = (df["close"] - df["SMA_50"]) / df["SMA_50"]

        # 2. RSI
        if "RSI_14" in df.columns:
            features["rsi"] = df["RSI_14"]

        # 3. MACD
        # MACD_12_26_9, MACDh_12_26_9 (ヒストグラム), MACDs_12_26_9 (シグナル)
        # pandas-ta の列名に依存するため、存在チェックを行う
        macd_col = "MACD_12_26_9"
        hist_col = "MACDh_12_26_9"
        if macd_col in df.columns:
            features["macd"] = df[macd_col]
        if hist_col in df.columns:
            features["macd_hist"] = df[hist_col]

        # 4. ボリンジャーバンド位置 (Band Width, %B)
        # BBU_20_2.0 (Upper), BBL_20_2.0 (Lower)
        upper_col = "BBU_20_2.0"
        lower_col = "BBL_20_2.0"
        if upper_col in df.columns and lower_col in df.columns:
            features["bb_width"] = (df[upper_col] - df[lower_col]) / df["SMA_20"]
            features["bb_position"] = (df["close"] - df[lower_col]) / (
                df[upper_col] - df[lower_col]
            )

        # 5. 出来高変化率
        features["volume_change"] = df["volume"].pct_change()

        # 欠損値を含む行を削除（計算初期の期間など）
        return features.dropna()

    def train(self, df: pd.DataFrame, target_days: int = 30) -> dict:
        """
        モデルを学習する。

        Args:
            df: 株価データ（テクニカル指標付き）
            target_days: 何日後の騰落を予測するか

        Returns:
            dict: 学習結果（精度など）
        """
        features = self.prepare_features(df)
        if features.empty:
            raise ValueError("学習可能なデータがありません")

        # ターゲット作成: N日後のリターン
        # shift(-N) で未来の価格を現在の行に持ってくる
        future_return = df["close"].shift(-target_days) / df["close"] - 1.0
        # 特徴量とインデックスを合わせる
        target = future_return[features.index]
        # ターゲットが NaN になる（直近データ）を除外
        valid_indices = target.dropna().index
        X = features.loc[valid_indices]
        y = target.loc[valid_indices]

        # 騰落クラスに変換（0: 下落, 1: 上昇）あるいは回帰
        # ここでは回帰（リターン予測）とする
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test)

        params = {
            "objective": "regression",
            "metric": "rmse",
            "boosting_type": "gbdt",
            "verbosity": -1,
        }

        self.model = lgb.train(
            params,
            train_data,
            valid_sets=[valid_data],
            # early_stopping_rounds=10, # LightGBM 4.0以降はcallback推奨だが簡易的に省略または警告無視
            num_boost_round=100,
            callbacks=[
                lgb.early_stopping(stopping_rounds=10),
                lgb.log_evaluation(period=0),  # ログ出力を抑制
            ],
        )

        return {
            "train_rmse": float(self.model.best_score["valid_0"]["rmse"]),
            "feature_importance": dict(
                zip(X.columns, self.model.feature_importance().tolist())
            ),
        }

    def predict(self, df: pd.DataFrame, target_days: int = 30) -> float:
        """
        最新データに基づいて将来のリターンを予測する。
        """
        if self.model is None:
            raise ValueError("モデルが学習されていません")

        features = self.prepare_features(df)
        if features.empty:
            return 0.0

        # 最新の行を使用
        latest_features = features.iloc[[-1]]
        prediction = self.model.predict(latest_features)[0]
        return float(prediction)
