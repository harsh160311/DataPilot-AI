import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.data_processor import data_processor
from app.services.insight_engine import insight_engine
from app.services.alert_engine import alert_engine
from app.services.ml_engine import ml_engine
from app.services.report_generator import report_generator

router = APIRouter()


@router.get("/summary/{session_id}")
async def get_report(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    insights = insight_engine.generate_insights(df)
    alerts = alert_engine.generate_alerts(df)

    predictions = []
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    for col in numeric_cols[:2]:
        try:
            result = ml_engine.predict(df, col, 5)
            if "error" not in result:
                predictions.append(result)
        except Exception:
            pass

    report = report_generator.generate_summary_report(df, insights, alerts, predictions)
    return report


@router.get("/text/{session_id}")
async def get_text_report(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    insights = insight_engine.generate_insights(df)
    alerts = alert_engine.generate_alerts(df)

    report_data = report_generator.generate_summary_report(df, insights, alerts, [])
    text = report_generator.generate_text_report(report_data)

    return Response(content=text, media_type="text/plain")


@router.get("/quality/{session_id}")
async def get_quality_score(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    quality = report_generator._calculate_quality_score(df)
    return quality
