from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.ai_engine import chat
from pydantic import BaseModel

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

@router.post("/chat")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    messages = [m.model_dump() for m in req.messages]
    reply = chat(messages, db)
    return {"reply": reply}
