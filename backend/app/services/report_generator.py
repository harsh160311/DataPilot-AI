import io
from datetime import datetime
from pandas import DataFrame
import pandas as pd

from app.services.data_processor import clean_nan


class ReportGenerator:
    def generate_summary_report(self, df: DataFrame, insights: list, alerts: list, predictions: list) -> dict:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        critical_findings = [i for i in insights if i.get("severity") == "critical"]
        warnings = [i for i in insights if i.get("severity") == "warning"]
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]

        report = {
            "title": "DataPilot AI - Auto Summary Report",
            "generated_at": datetime.utcnow().isoformat(),
            "dataset_summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": len(numeric_cols),
                "categorical_columns": len(categorical_cols),
                "missing_values": int(df.isna().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
            },
            "key_findings": {
                "critical_count": len(critical_findings) + len(critical_alerts),
                "warning_count": len(warnings),
                "total_insights": len(insights),
                "total_alerts": len(alerts),
            },
            "top_insights": insights[:5] if insights else [],
            "critical_alerts": alerts[:5] if alerts else [],
            "predictions_summary": predictions[:3] if predictions else [],
            "recommendations": self._generate_recommendations(df, insights, alerts),
            "quality_score": self._calculate_quality_score(df),
        }
        return clean_nan(report)

    def _generate_recommendations(self, df: DataFrame, insights: list, alerts: list) -> list:
        recommendations = []
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if df.isna().sum().sum() > 0:
            recommendations.append("Clean missing values to improve data quality and model accuracy.")
        if df.duplicated().sum() > 0:
            recommendations.append(f"Remove {df.duplicated().sum()} duplicate rows.")
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            high_corr = []
            for i, c1 in enumerate(numeric_cols):
                for c2 in numeric_cols[i + 1:]:
                    if abs(corr_matrix.loc[c1, c2]) > 0.9:
                        high_corr.append((c1, c2))
            if high_corr:
                cols = ", ".join([f"'{c1}' & '{c2}'" for c1, c2 in high_corr[:3]])
                recommendations.append(f"Consider removing redundant features: {cols}.")

        if len(alerts) > 3:
            recommendations.append("Investigate anomalies and trend changes in the data.")

        recommendations.append("Use the Prediction Engine to forecast key metrics.")
        recommendations.append("Explore the AI Chat Assistant for natural language data queries.")

        return recommendations[:5]

    def _calculate_quality_score(self, df: DataFrame) -> dict:
        total_cells = len(df) * len(df.columns)
        if total_cells == 0:
            return {"score": 0, "grade": "F"}

        missing_ratio = df.isna().sum().sum() / total_cells
        duplicate_ratio = df.duplicated().sum() / len(df) if len(df) > 0 else 0

        score = 100
        score -= missing_ratio * 50
        score -= duplicate_ratio * 30

        numeric_cols = df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 1:
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                if iqr == 0:
                    score -= 5

        score = max(0, min(100, score))
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"

        return {"score": round(score, 1), "grade": grade}

    def generate_text_report(self, report: dict) -> str:
        lines = [
            "=" * 60,
            f"  {report['title']}",
            "=" * 60,
            f"  Generated: {report['generated_at']}",
            "",
            "─" * 60,
            "  DATASET SUMMARY",
            "─" * 60,
            f"  Rows: {report['dataset_summary']['total_rows']:,}",
            f"  Columns: {report['dataset_summary']['total_columns']}",
            f"  Numeric: {report['dataset_summary']['numeric_columns']}",
            f"  Categorical: {report['dataset_summary']['categorical_columns']}",
            f"  Missing Values: {report['dataset_summary']['missing_values']:,}",
            f"  Duplicates: {report['dataset_summary']['duplicate_rows']:,}",
            "",
            f"  Quality Score: {report.get('quality_score', {}).get('score', 'N/A')} / 100",
            f"  Grade: {report.get('quality_score', {}).get('grade', 'N/A')}",
        ]

        if report.get("top_insights"):
            lines.extend([
                "",
                "─" * 60,
                "  KEY INSIGHTS",
                "─" * 60,
            ])
            for ins in report["top_insights"]:
                lines.append(f"  [{ins['severity'].upper()}] {ins['title']}")
                lines.append(f"  {ins['description']}")
                lines.append("")

        if report.get("critical_alerts"):
            lines.extend([
                "─" * 60,
                "  ALERTS",
                "─" * 60,
            ])
            for alert in report["critical_alerts"]:
                lines.append(f"  [{alert['severity'].upper()}] {alert['message']}")

        if report.get("recommendations"):
            lines.extend([
                "",
                "─" * 60,
                "  RECOMMENDATIONS",
                "─" * 60,
            ])
            for i, rec in enumerate(report["recommendations"], 1):
                lines.append(f"  {i}. {rec}")

        lines.extend([
            "",
            "═" * 60,
            "  Generated by DataPilot AI",
            "═" * 60,
        ])

        return "\n".join(lines)


report_generator = ReportGenerator()
