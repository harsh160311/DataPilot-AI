from fastapi import APIRouter, HTTPException

from app.services.data_processor import data_processor, clean_nan
from app.services.gpu_accelerator import gpu_accelerator

router = APIRouter()


@router.get("/summary/{session_id}")
async def get_summary(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")
    return data_processor.get_summary(df)


@router.post("/clean/{session_id}")
async def clean_data(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    cleaned_df, result = data_processor.clean_data(df)
    data_processor.save_session_data(session_id, cleaned_df, data_processor.get_session_data(session_id)["filename"])
    return result


@router.get("/describe/{session_id}")
async def describe_data(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    gpu_desc = gpu_accelerator.describe_gpu(df)
    if gpu_desc is not None:
        return clean_nan(gpu_desc.to_dict())

    numeric_cols = df.select_dtypes(include=["number"])
    if numeric_cols.empty:
        return {"message": "No numeric columns to describe"}
    return clean_nan(numeric_cols.describe().to_dict())


@router.get("/columns/{session_id}")
async def get_columns(session_id: str):
    df = data_processor.get_dataframe(session_id)
    if df is None:
        raise HTTPException(404, "Session not found")

    return {
        "columns": [
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "nulls": int(df[col].isna().sum()),
                "unique": int(df[col].nunique()),
            }
            for col in df.columns
        ]
    }


@router.get("/gpu-status")
async def gpu_status():
    return gpu_accelerator.get_stats()
