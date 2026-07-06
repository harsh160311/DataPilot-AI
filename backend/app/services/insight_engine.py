import pandas as pd
from pandas import DataFrame
import numpy as np
from scipy import stats

from app.services.data_processor import clean_nan


class InsightEngine:
    def generate_insights(self, df: DataFrame) -> list[dict]:
        insights = []
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 2:
                continue

            mean_val = series.mean()
            median_val = series.median()
            skewness = series.skew()

            if abs(skewness) > 1:
                direction = "right" if skewness > 0 else "left"
                insights.append({
                    "type": "distribution",
                    "title": f"Skewed distribution detected in '{col}'",
                    "description": f"Column '{col}' has a {direction}-skewed distribution (skewness: {skewness:.2f}). Mean ({mean_val:.2f}) differs from median ({median_val:.2f}).",
                    "severity": "info",
                    "value": {"mean": float(mean_val), "median": float(median_val), "skewness": float(skewness)},
                    "recommendation": f"Consider log transformation for '{col}' if using in regression models.",
                })

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 1:
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                outlier_mask = (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)
                outlier_pct = outlier_mask.mean() * 100
                if outlier_pct > 5:
                    insights.append({
                        "type": "outlier",
                        "title": f"Outliers detected in '{col}'",
                        "description": f"{outlier_pct:.1f}% of values in '{col}' are outliers, which may affect analysis reliability.",
                        "severity": "warning",
                        "value": {"outlier_percentage": round(outlier_pct, 1)},
                        "recommendation": "Review outlier values and consider capping or removing extreme values.",
                    })

        if len(categorical_cols) >= 2:
            for i, col1 in enumerate(categorical_cols):
                for col2 in categorical_cols[i + 1:]:
                    if len(categorical_cols) > 4:
                        break
                    cross = pd.crosstab(df[col1], df[col2])
                    if cross.size > 1:
                        chi2, p_val, _, _ = stats.chi2_contingency(cross)
                        if p_val < 0.05:
                            insights.append({
                                "type": "correlation",
                                "title": f"Strong association: '{col1}' vs '{col2}'",
                                "description": f"Statistical test shows significant relationship between '{col1}' and '{col2}' (p-value: {p_val:.4f}).",
                                "severity": "info",
                                "value": {"chi2": float(chi2), "p_value": float(p_val)},
                                "recommendation": "Consider this relationship when building predictive models.",
                            })

        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i + 1:]:
                    corr_val = corr_matrix.loc[col1, col2]
                    if abs(corr_val) > 0.7:
                        direction = "positive" if corr_val > 0 else "negative"
                        insights.append({
                            "type": "correlation",
                            "title": f"Strong {direction} correlation: '{col1}' vs '{col2}'",
                            "description": f"'{col1}' and '{col2}' have a {direction} correlation of {corr_val:.2f}.",
                            "severity": "info",
                            "value": {"correlation": float(corr_val)},
                            "recommendation": f"These variables may be redundant; consider feature selection.",
                        })

        if datetime_cols:
            for col in datetime_cols:
                series = df[col].dropna()
                if len(series) > 1:
                    date_range = series.max() - series.min()
                    insights.append({
                        "type": "temporal",
                        "title": f"Time range detected in '{col}'",
                        "description": f"Data spans {date_range.days} days from {series.min().strftime('%Y-%m-%d')} to {series.max().strftime('%Y-%m-%d')}.",
                        "severity": "info",
                        "value": {"min_date": str(series.min()), "max_date": str(series.max()), "days_span": date_range.days},
                    })

        if df.isna().sum().sum() > 0:
            null_cols = df.isna().sum()
            null_cols = null_cols[null_cols > 0].sort_values(ascending=False)
            top_null = null_cols.head(3)
            for col, count in top_null.items():
                pct = count / len(df) * 100
                if pct > 10:
                    insights.append({
                        "type": "data_quality",
                        "title": f"High missing values in '{col}'",
                        "description": f"Column '{col}' has {count} missing values ({pct:.1f}% of total).",
                        "severity": "warning",
                        "value": {"missing_count": int(count), "missing_percentage": round(pct, 1)},
                        "recommendation": "Consider imputation or removal of this column.",
                    })

        if len(numeric_cols) > 0:
            top_growth_col = max(numeric_cols, key=lambda c: df[c].std() if df[c].std() else 0)
            insights.append({
                "type": "variance",
                "title": f"Highest variance: '{top_growth_col}'",
                "description": f"'{top_growth_col}' has the highest variance (std: {df[top_growth_col].std():.2f}), indicating significant fluctuations.",
                "severity": "info",
                "value": {"column": top_growth_col, "std": float(df[top_growth_col].std())},
            })

        for col in categorical_cols:
            value_counts = df[col].value_counts()
            if len(value_counts) > 0:
                top_val = value_counts.index[0]
                top_pct = value_counts.iloc[0] / len(df) * 100
                if top_pct > 50:
                    insights.append({
                        "type": "dominance",
                        "title": f"'{top_val}' dominates '{col}'",
                        "description": f"'{top_val}' represents {top_pct:.1f}% of all values in '{col}'.",
                        "severity": "info",
                        "value": {"dominant_value": str(top_val), "percentage": round(top_pct, 1)},
                    })

        insights.sort(key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x["severity"], 3))

        return clean_nan(insights[:20])


insight_engine = InsightEngine()
