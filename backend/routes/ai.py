from fastapi import APIRouter
from pydantic import BaseModel

from backend.rag.retriever import retriever
from backend.services.gemini_service import gemini_service
from backend.services.session_manager import session_manager
from backend.services.conversation_engine import conversation_engine

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
def chat(request: ChatRequest):

    response = conversation_engine.process(
        request.session_id,
        request.message
    )

    return {
        "response": response
    }
    
@router.post("/session")
def create_session():

    session_id = session_manager.create_session()

    return {
        "session_id": session_id
    }


@router.get("/session/{session_id}")
def get_session(session_id: str):

    return session_manager.get(session_id)