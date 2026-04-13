"""
ai.py — AI assistant chat endpoint.

POST /api/ai/chat — accepts a message and conversation history,
                    returns Claude's response with live fleet context
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import require_manager
from ai_assistant import chat

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=schemas.ChatResponse)
def ai_chat(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Send a message to the AI assistant.
    The assistant has access to live fleet data to answer accurately.
    Conversation history is passed from the frontend and not stored in the database.
    """
    response_text = chat(
        message=request.message,
        history=[m.model_dump() for m in request.history],
        db=db,
    )
    return schemas.ChatResponse(response=response_text)
