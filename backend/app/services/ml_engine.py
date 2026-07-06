import warnings
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score

from app.config import settings
from app.services.data_processor import clean_nan
from app.services.gpu_accelerator import gpu_accelerator

warnings.filterwarnings("ignore")


class MLEngine:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scaler = StandardScaler()

    def _prepare_data(self, df: DataFrame, target_col: str):
        df = df.copy()
        df = df.dropna(subset=[target_col])

        feature_cols = [c for c in df.columns if c != target_col]

        for col in feature_cols:
            if df[col].dtype == "object" or df[col].dtype.name == "category":
                le = LabelEncoder()
                df[col] = df[col].astype(str)
                df[col] = le.fit_transform(df[col])
                self.encoders[col] = le
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[f"{col}_year"] = df[col].dt.year
                df[f"{col}_month"] = df[col].dt.month
                df[f"{col}_day"] = df[col].dt.day
                df = df.drop(columns=[col])

        feature_cols = [c for c in df.columns if c != target_col]
        feature_cols = [c for c in feature_cols if df[c].dtype in ("int64", "float64")]

        X = df[feature_cols].fillna(0)
        y = df[target_col]

        return X, y, feature_cols

    def train_model(self, df: DataFrame, target_col: str, model_type: str = "auto"):
        X, y, features = self._prepare_data(df, target_col)

        if len(X) < 10:
            return {"error": "Too few samples for training (min 10 required)"}

        test_size = 0.2 if len(X) >= 50 else max(0.1, 1.0 / len(X))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        is_classification = y.dtype == "object" or y.nunique() < 10

        if model_type == "auto":
            model_type = "classification" if is_classification else "regression"

        if model_type == "classification":
            model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        else:
            if settings.ENABLE_GPU and gpu_accelerator._cuml is not None:
                try:
                    from cuml.ensemble import RandomForestRegressor as cumlRF
                    model = cumlRF(n_estimators=100, random_state=42)
                except Exception:
                    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            else:
                try:
                    from xgboost import XGBRegressor
                    model = XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                except ImportError:
                    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if model_type == "classification":
            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "type": "classification",
            }
        else:
            metrics = {
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "mse": float(mean_squared_error(y_test, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                "r2": float(r2_score(y_test, y_pred)),
                "type": "regression",
            }

        feature_importance = []
        if hasattr(model, "feature_importances_"):
            for name, imp in zip(features, model.feature_importances_):
                feature_importance.append({"feature": name, "importance": float(imp)})
            feature_importance.sort(key=lambda x: x["importance"], reverse=True)

        self.models[target_col] = model

        return clean_nan({
            "target": target_col,
            "model_type": model_type,
            "metrics": metrics,
            "feature_importance": feature_importance[:20],
            "training_samples": len(X_train),
            "test_samples": len(X_test),
        })

    def predict(self, df: DataFrame, target_col: str, periods: int = 5):
        if target_col not in self.models:
            result = self.train_model(df, target_col)
            if "error" in result:
                return result

        model = self.models.get(target_col)
        if model is None:
            return {"error": f"No model trained for '{target_col}'"}

        X, y, features = self._prepare_data(df, target_col)
        X = X[features] if all(f in X for f in features) else X

        last_row = X.iloc[-1:].copy()
        forecasts = []

        for i in range(periods):
            pred = model.predict(last_row)[0]
            forecasts.append({
                "period": i + 1,
                "predicted_value": float(pred),
            })
            for col in last_row.columns:
                noise = np.random.normal(0, abs(last_row[col].values[0] * 0.01))
                last_row[col] = last_row[col].values[0] + noise

        return clean_nan({
            "target": target_col,
            "forecasts": forecasts,
            "model_trained": target_col in self.models,
        })

    def detect_anomalies(self, df: DataFrame, column: str, threshold: float = 2.0):
        if column not in df.columns:
            return {"error": f"Column '{column}' not found"}

        if not pd.api.types.is_numeric_dtype(df[column]):
            return {"error": f"Column '{column}' is not numeric"}

        values = df[column].dropna()
        mean = values.mean()
        std = values.std()

        if std == 0:
            return {"anomalies": [], "message": "No variance in data"}

        z_scores = np.abs((values - mean) / std)
        anomaly_indices = np.where(z_scores > threshold)[0]

        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                "index": int(idx),
                "value": float(values.iloc[idx]),
                "z_score": float(z_scores.iloc[idx]),
                "direction": "high" if values.iloc[idx] > mean else "low",
            })

        return clean_nan({
            "column": column,
            "mean": float(mean),
            "std": float(std),
            "threshold": threshold,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:50],
        })


ml_engine = MLEngine()
