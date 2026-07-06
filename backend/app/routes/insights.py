from fastapi import APIRouter, HTTPException

from app.services.data_processor import data_processor
from app.services.insight_engine import insight_engine

router = APIRouter()


@router.get("/{session_id}")
async def get_insights(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    insights = insight_engine.generate_insights(df)
    return {"insights": insights, "count": len(insights)}


@router.get("/trends/{session_id}")
async def get_trends(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    trends = []
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if datetime_cols and numeric_cols:
        time_col = datetime_cols[0]
        for num_col in numeric_cols[:3]:
            trend_data = df[[time_col, num_col]].dropna().sort_values(time_col).tail(100)
            if len(trend_data) > 1:
                first_val = trend_data[num_col].iloc[0]
                last_val = trend_data[num_col].iloc[-1]
                if first_val != 0:
                    pct_change = ((last_val - first_val) / abs(first_val)) * 100
                    trends.append({
                        "column": num_col,
                        "direction": "up" if pct_change > 0 else "down",
                        "change_percent": round(pct_change, 1),
                        "first_value": float(first_val),
                        "last_value": float(last_val),
                    })

    return {"trends": trends}
