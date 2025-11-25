from fastapi import APIRouter

from app.config import settings
from app.models.schema import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ResponseOutput,
    ResponseRequest,
)
from app.services.openai_service import (
    create_chat_completion,
    create_embedding,
    create_model_response,
)

router = APIRouter()


@router.get("/health", summary="Liveness probe", responses={200: {"description": "Service is up"}})
async def health() -> dict:
    """Asynchronous health endpoint to verify the service is running."""
    return {"status": "ok"}


@router.post(
    "/chat/complete",
    response_model=ChatResponse,
    summary="Create a chat completion via OpenAI",
    responses={
        200: {
            "description": "Successful chat completion",
            "content": {"application/json": {"example": {"response": "Hello there!"}}},
        },
        400: {"description": "Validation error"},
        502: {"description": "Failed to fetch completion from OpenAI"},
    },
)
async def chat_complete(payload: ChatRequest) -> ChatResponse:
    """
    Forward the user prompt to OpenAI and return the model's reply.
    The request model enforces input structure and defaults.
    """
    model_name = payload.model or settings.openai_model
    completion_text = await create_chat_completion(prompt=payload.prompt, model=model_name)
    return ChatResponse(response=completion_text)


@router.post(
    "/embeddings",
    response_model=EmbeddingResponse,
    summary="Generate an embedding vector via OpenAI",
    responses={
        200: {
            "description": "Embedding generated",
            "content": {
                "application/json": {
                    "example": {
                        "embedding": [0.01, -0.02, 0.03],
                    }
                }
            },
        },
        400: {"description": "Validation error"},
        502: {"description": "Failed to fetch embedding from OpenAI"},
    },
)
async def generate_embedding(payload: EmbeddingRequest) -> EmbeddingResponse:
    """
    Create an embedding for the provided text using the specified model.
    """
    model_name = payload.model or "text-embedding-3-small"
    vector = await create_embedding(text=payload.text, model=model_name)
    return EmbeddingResponse(embedding=vector)


@router.post(
    "/responses",
    response_model=ResponseOutput,
    summary="Call the OpenAI Responses API",
    responses={
        200: {
            "description": "Model response generated",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Here is the generated reply.",
                        "response_id": "resp_123",
                    }
                }
            },
        },
        400: {"description": "Validation error"},
        500: {"description": "Configuration error"},
        502: {"description": "Upstream error from OpenAI"},
    },
)
async def create_response(payload: ResponseRequest) -> ResponseOutput:
    """
    Generate a model response using OpenAI's Responses API.
    """
    model_name = payload.model or settings.openai_model
    output_text, response_id = await create_model_response(user_input=payload.input, model=model_name)
    return ResponseOutput(response=output_text, response_id=response_id)
