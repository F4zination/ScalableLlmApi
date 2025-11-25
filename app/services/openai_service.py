import asyncio

import openai
from fastapi import HTTPException, status

from app.config import settings

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - fallback for older SDK versions
    OpenAI = None  # type: ignore


def _init_openai_client() -> None:
    """
    Initialize the OpenAI client with the configured API key.
    Called on import to ensure downstream calls have a key set.
    """
    openai.api_key = settings.openai_api_key


_init_openai_client()
_client = OpenAI(api_key=settings.openai_api_key) if OpenAI else None


async def create_chat_completion(prompt: str, model: str) -> str:
    """
    Call the OpenAI ChatCompletion endpoint in a worker thread.
    Keeps FastAPI's event loop free while the SDK performs network I/O.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured",
        )

    def _request() -> dict:
        return openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

    try:
        response = await asyncio.to_thread(_request)
        message = response["choices"][0]["message"]["content"]
        return message.strip()
    except Exception as exc:
        # Surface a generic message to the client while preserving context for logs.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch completion from OpenAI",
        ) from exc


async def create_embedding(text: str, model: str) -> list[float]:
    """
    Call the OpenAI Embedding endpoint in a worker thread.
    Returns the first embedding vector produced by the model.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured",
        )

    def _request() -> dict:
        return openai.Embedding.create(
            input=text,
            model=model,
        )

    try:
        response = await asyncio.to_thread(_request)
        embedding = response["data"][0]["embedding"]
        return embedding
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch embedding from OpenAI",
        ) from exc


async def create_model_response(user_input: str, model: str) -> tuple[str, str]:
    """
    Call the OpenAI Responses API using the newer client interface.
    Returns the generated text and response ID.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured",
        )

    if not _client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI client not available for Responses API",
        )

    def _request():
        return _client.responses.create(model=model, input=user_input)

    try:
        response = await asyncio.to_thread(_request)
        output_text = getattr(response, "output_text", None)

        if not output_text:
            output = getattr(response, "output", None) or {}
            if output:
                first = output[0]
                content = getattr(first, "content", None) or first.get("content", [])
                if content:
                    item = content[0]
                    output_text = getattr(item, "text", None) or item.get("text")

        if not output_text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OpenAI response did not include text output",
            )

        response_id = getattr(response, "id", "")
        if not response_id and isinstance(response, dict):
            response_id = response.get("id", "")
        return output_text.strip(), response_id
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch response from OpenAI",
        ) from exc
