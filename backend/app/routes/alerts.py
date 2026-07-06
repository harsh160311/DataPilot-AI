import pandas as pd
from fastapi import APIRouter, HTTPException

from app.services.data_processor import data_processor
from app.services.alert_engine import alert_engine

router = APIRouter()


@router.get("/{session_id}")
async def get_alerts(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    alerts = alert_engine.generate_alerts(df)
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/rankings/{session_id}")
async def get_rankings(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    rankings = []
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        for num_col in numeric_cols[:3]:
            if pd.api.types.is_numeric_dtype(df[num_col]):
                ranked = df.groupby(cat_col)[num_col].sum().reset_index()
                ranked = ranked.sort_values(num_col, ascending=False).head(10)
                rankings.append({
                    "category": cat_col,
                    "metric": num_col,
                    "rankings": [
                        {"rank": i + 1, "label": str(row[cat_col]), "value": float(row[num_col])}
                        for i, (_, row) in enumerate(ranked.iterrows())
                    ],
                })

    return {"rankings": rankings}
