from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        status="stub",
        message=(
            "KnowFlow FastAPI S1 skeleton is running. "
            "Domain Router, Permission, Version and RAG are not implemented yet."
        ),
        query=request.query,
    )