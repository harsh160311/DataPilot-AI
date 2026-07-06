from fastapi import APIRouter, HTTPException

from app.services.data_processor import data_processor
from app.services.chat_assistant import chat_assistant
from app.models.schemas import ChatRequest

router = APIRouter()


@router.post("/ask/{session_id}")
async def ask_question(session_id: str, request: ChatRequest):
    df = data_processor.get_dataframe(session_id)
    summary = {}

    if df is None:
        raise HTTPException(404, "Session not found or dataset expired")

    session_data = data_processor.get_session_data(session_id)
    if session_data:
        summary = data_processor.get_summary(df)

    response = chat_assistant.ask(
        message=request.message,
        df=df,
        summary=summary,
        history=request.conversation_history,
    )

    return response
