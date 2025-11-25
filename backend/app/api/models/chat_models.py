from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    local_sources: list
    web_sources_verified: list
    web_sources_unverified: list
    intent: str
