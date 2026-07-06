from fastapi import APIRouter, HTTPException, Query

from app.services.data_processor import data_processor
from app.services.ml_engine import ml_engine

router = APIRouter()


@router.get("/train/{session_id}")
async def train_model(session_id: str, target: str = Query(..., description="Target column for prediction")):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")
    if target not in df.columns:
        raise HTTPException(400, f"Column '{target}' not found in dataset")

    result = ml_engine.train_model(df, target)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.get("/forecast/{session_id}")
async def forecast(session_id: str, target: str = Query(...), periods: int = Query(5, ge=1, le=30)):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")
    if target not in df.columns:
        raise HTTPException(400, f"Column '{target}' not found in dataset")

    result = ml_engine.predict(df, target, periods)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.get("/anomalies/{session_id}")
async def detect_anomalies(
    session_id: str,
    column: str = Query(...),
    threshold: float = Query(2.0, ge=0.5, le=5.0),
):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    result = ml_engine.detect_anomalies(df, column, threshold)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
