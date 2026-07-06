import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.services.data_processor import data_processor, clean_nan

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Supported: {settings.ALLOWED_EXTENSIONS}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    session_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{session_id}{ext}")

    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        df = data_processor.parse_file(file_path, file.filename)
        data_processor.save_session_data(session_id, df, file.filename)
        summary = data_processor.get_summary(df)

        return clean_nan({
            "session_id": session_id,
            "file_name": file.filename,
            "file_type": ext[1:],
            "summary": summary,
            "columns": summary["column_details"],
            "sample": df.head(10).to_dict(orient="records"),
        })
    except Exception as e:
        raise HTTPException(500, f"Error processing file: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    session = data_processor.get_session_data(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    data_processor.delete_session(session_id)
    return {"message": "Session deleted successfully"}
