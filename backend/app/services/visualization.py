import json
import base64
import io
from typing import Optional
from pandas import DataFrame
import pandas as pd

from app.services.data_processor import clean_nan


class VisualizationService:
    def generate_chart_data(self, df: DataFrame, chart_type: str, x_col: str, y_col: Optional[str] = None) -> dict:
        result = {"type": chart_type, "data": []}

        if chart_type == "line":
            if y_col:
                if pd.api.types.is_datetime64_any_dtype(df[x_col]):
                    df = df.sort_values(x_col)
                result["data"] = df[[x_col, y_col]].dropna().head(500).to_dict(orient="records")
            else:
                numeric_cols = df.select_dtypes(include=["number"]).columns[:3]
                subset = df[[x_col] + list(numeric_cols)].dropna().head(500)
                result["data"] = subset.to_dict(orient="records")
                result["series"] = list(numeric_cols)

        elif chart_type == "bar":
            if y_col:
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    grouped = df.groupby(x_col)[y_col].sum().reset_index().head(50)
                else:
                    grouped = df[x_col].value_counts().reset_index()
                    grouped.columns = [x_col, "count"]
                    y_col = "count"
                result["data"] = grouped.to_dict(orient="records")
            else:
                counts = df[x_col].value_counts().reset_index()
                counts.columns = [x_col, "count"]
                result["data"] = counts.head(50).to_dict(orient="records")
                y_col = "count"

        elif chart_type == "pie":
            counts = df[x_col].value_counts().reset_index()
            counts.columns = ["label", "value"]
            result["data"] = counts.head(20).to_dict(orient="records")

        elif chart_type == "heatmap":
            numeric_cols = df.select_dtypes(include=["number"]).columns[:10]
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr().round(2)
                result["data"] = {
                    "columns": list(corr.columns),
                    "index": list(corr.index),
                    "values": corr.values.tolist(),
                }

        elif chart_type == "scatter":
            if x_col and y_col:
                result["data"] = df[[x_col, y_col]].dropna().head(1000).to_dict(orient="records")

        elif chart_type == "histogram":
            if x_col:
                hist_data = df[x_col].dropna()
                result["data"] = {
                    "values": hist_data.tolist()[:5000],
                    "bins": 30,
                }

        return result

    def generate_dashboard(self, df: DataFrame) -> dict:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        charts = []
        time_col = datetime_cols[0] if datetime_cols else None
        top_cat = categorical_cols[0] if categorical_cols else None
        top_num = numeric_cols[0] if numeric_cols else None
        second_num = numeric_cols[1] if len(numeric_cols) > 1 else None

        if time_col and top_num:
            chart = self.generate_chart_data(df, "line", time_col, top_num)
            chart["title"] = f"{top_num} over Time"
            charts.append(chart)

        if top_cat and top_num:
            chart = self.generate_chart_data(df, "bar", top_cat, top_num)
            chart["title"] = f"{top_num} by {top_cat}"
            charts.append(chart)

        if top_cat:
            chart = self.generate_chart_data(df, "pie", top_cat)
            chart["title"] = f"Distribution of {top_cat}"
            charts.append(chart)

        if len(numeric_cols) >= 3:
            chart = self.generate_chart_data(df, "heatmap", None, None)
            chart["title"] = "Feature Correlation Heatmap"
            charts.append(chart)

        if top_num and second_num:
            chart = self.generate_chart_data(df, "scatter", top_num, second_num)
            chart["title"] = f"{top_num} vs {second_num}"
            charts.append(chart)

        if top_num:
            chart = self.generate_chart_data(df, "histogram", top_num)
            chart["title"] = f"Distribution of {top_num}"
            charts.append(chart)

        kpis = []
        for col in numeric_cols[:4]:
            mean_val = df[col].mean()
            std_val = df[col].std()
            kpis.append({
                "label": f"Avg {col}",
                "value": round(mean_val, 2) if df[col].count() > 0 and not pd.isna(mean_val) else 0,
                "change": round(std_val / mean_val * 100, 1) if mean_val and mean_val != 0 and not pd.isna(std_val / mean_val * 100) else 0,
                "format": "number",
            })

        if time_col:
            kpis.append({
                "label": "Date Range",
                "value": f"{df[time_col].min().strftime('%Y-%m-%d')} to {df[time_col].max().strftime('%Y-%m-%d')}",
                "change": 0,
                "format": "text",
            })

        kpis.append({
            "label": "Total Rows",
            "value": len(df),
            "change": 0,
            "format": "number",
        })

        return clean_nan({
            "kpis": kpis,
            "charts": charts,
            "layout": "grid",
        })


visualization_service = VisualizationService()
