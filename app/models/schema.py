from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to send to the model")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Completion text returned from OpenAI")
