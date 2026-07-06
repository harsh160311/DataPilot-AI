from fastapi import APIRouter, HTTPException, Query

from app.services.data_processor import data_processor
from app.services.visualization import visualization_service

router = APIRouter()


@router.get("/{session_id}")
async def get_dashboard(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    dashboard = visualization_service.generate_dashboard(df)
    return dashboard


@router.get("/chart/{session_id}")
async def get_chart(
    session_id: str,
    chart_type: str = Query("bar"),
    x_col: str = Query(...),
    y_col: str = Query(None),
):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")
    if x_col not in df.columns:
        raise HTTPException(400, f"Column '{x_col}' not found")
    if y_col and y_col not in df.columns:
        raise HTTPException(400, f"Column '{y_col}' not found")

    chart_data = visualization_service.generate_chart_data(df, chart_type, x_col, y_col)
    return chart_data


@router.get("/kpis/{session_id}")
async def get_kpis(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    dashboard = visualization_service.generate_dashboard(df)
    return {"kpis": dashboard["kpis"]}
