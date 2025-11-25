import asyncio
from typing import Callable

import openai
from fastapi import HTTPException, status

from app.config import settings


def _init_openai_client() -> None:
    """
    Initialize the OpenAI client with the configured API key.
    Called on import to ensure downstream calls have a key set.
    """
    openai.api_key = settings.openai_api_key


_init_openai_client()


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
