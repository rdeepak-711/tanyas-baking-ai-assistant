from fastapi import APIRouter, HTTPException
from app.api.models.chat_models import ChatRequest, ChatResponse
from app.services.llm_engine import answer_question

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(payload: ChatRequest):

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = answer_question(payload.question)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return ChatResponse(
        answer=result["answer"],
        local_sources=result["sources"]["local"],
        web_sources_verified=result["sources"]["web_verified"],
        web_sources_unverified=result["sources"]["web_unverified"],
        intent=result["intent"]
    )
