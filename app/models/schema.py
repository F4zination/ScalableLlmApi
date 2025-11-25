from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to send to the model")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Completion text returned from OpenAI")


class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to generate embeddings for")
    model: str = Field(default="text-embedding-3-small", description="Embedding model to use")


class EmbeddingResponse(BaseModel):
    embedding: List[float] = Field(..., description="Vector representation for the input text")


class ResponseRequest(BaseModel):
    input: str = Field(..., description="Input prompt to generate a model response")
    model: str = Field(default="gpt-4o-mini", description="Model ID for the Responses API")


class ResponseOutput(BaseModel):
    response: str = Field(..., description="Generated output from the Responses API")
    response_id: str = Field(..., description="ID of the created response object")
