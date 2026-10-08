"""Chat route handling multilingual voice & text queries for APMC price advice."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.nlp_service import process_chat_message

router = APIRouter(prefix="/api", tags=["Chat & NLP"])


class ChatRequest(BaseModel):
    message: str = Field(..., example="Pune me 20 quintal tomato kaha bechu?")
    language: Optional[str] = Field(None, example="hi")
    session_id: Optional[str] = Field(None, example="user-session-123")


class ChatResponse(BaseModel):
    reply: str
    intent: str
    entities: Dict[str, Any]
    missing_field: Optional[str] = None
    follow_up_needed: bool = False
    data: Optional[Any] = None
    language: str


@router.post("/chat", response_model=ChatResponse)
def handle_chat_message(payload: ChatRequest):
    """Processes user queries in English, Hindi, or Marathi.

    Extracts crop, quantity, location, and intent using Gemini or deterministic NLP,
    asks ONE follow-up if an essential entity is missing, and replies using real
    economic calculations from the engine.
    """
    clean_msg = payload.message.strip()
    if not clean_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        result = process_chat_message(
            message=clean_msg,
            explicit_language=payload.language
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(exc)}")
