from fastapi import APIRouter

from app.config import settings
from app.models.schema import ChatRequest, ChatResponse
from app.services.openai_service import create_chat_completion

router = APIRouter()


@router.post("/chat/complete", response_model=ChatResponse)
async def chat_complete(payload: ChatRequest) -> ChatResponse:
    """
    Forward the user prompt to OpenAI and return the model's reply.
    The request model enforces input structure and defaults.
    """
    model_name = payload.model or settings.openai_model
    completion_text = await create_chat_completion(prompt=payload.prompt, model=model_name)
    return ChatResponse(response=completion_text)
