import pandas as pd
from pandas import DataFrame
from datetime import datetime

from app.services.data_processor import clean_nan


class AlertEngine:
    def generate_alerts(self, df: DataFrame) -> list[dict]:
        alerts = []
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 10:
                continue

            mean = series.mean()
            std = series.std()
            if std == 0:
                continue

            last_val = series.iloc[-1]
            last_few = series.iloc[-5:]
            prev_avg = series.iloc[:-5].mean() if len(series) > 5 else mean

            if prev_avg != 0:
                pct_change = ((last_few.mean() - prev_avg) / abs(prev_avg)) * 100
            else:
                pct_change = 0

            z_score = abs((last_val - mean) / std)

            if z_score > 3:
                direction = "spike" if last_val > mean else "drop"
                alerts.append({
                    "type": "anomaly",
                    "message": f"Anomaly detected in '{col}': {direction} detected (z-score: {z_score:.2f})",
                    "severity": "critical",
                    "column": col,
                    "value": float(last_val),
                    "threshold": float(mean + 3 * std if last_val > mean else mean - 3 * std),
                    "timestamp": datetime.utcnow().isoformat(),
                })

            if abs(pct_change) > 20:
                direction = "increased" if pct_change > 0 else "dropped"
                alerts.append({
                    "type": "trend_change",
                    "message": f"Significant trend change: '{col}' {direction} by {abs(pct_change):.1f}% in recent records",
                    "severity": "warning",
                    "column": col,
                    "value": float(last_few.mean()),
                    "threshold": float(prev_avg),
                    "timestamp": datetime.utcnow().isoformat(),
                })

        if len(numeric_cols) >= 2:
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i + 1:]:
                    corr = df[col1].corr(df[col2])
                    if abs(corr) > 0.95:
                        alerts.append({
                            "type": "correlation_alert",
                            "message": f"Very high correlation ({corr:.2f}) between '{col1}' and '{col2}'",
                            "severity": "info",
                            "column": f"{col1} - {col2}",
                            "value": float(corr),
                            "threshold": 0.95,
                            "timestamp": datetime.utcnow().isoformat(),
                        })

        return clean_nan(alerts)


alert_engine = AlertEngine()
