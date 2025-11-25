from fastapi import FastAPI

from app.api.routes import router

# Initialize the FastAPI application.
app = FastAPI(title="OpenAI Chat API", version="0.1.0")

# Register API routes.
app.include_router(router)
