# ScalableLlmApi

A minimal FastAPI service that proxies chat completions to OpenAI. Built for Python 3.10+ with clean separation between API layer, schemas, configuration, and the OpenAI integration.

## Setup

1. Install dependencies (ideally inside a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment:
   ```bash
   cp .env.example .env
   # then edit .env to set OPENAI_API_KEY (and optionally OPENAI_MODEL)
   ```

## Running the server

```bash
uvicorn app.main:app --reload
```

The app exposes:
- `POST /chat/complete` for chat completions
- `POST /embeddings` for embedding vectors
- `POST /responses` for the Responses API (text out; supports image/text in via OpenAI)
- `GET /health` for liveness

## Example request

```bash
curl -X POST http://localhost:8000/chat/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Give me a three-sentence summary of FastAPI.",
    "model": "gpt-4o-mini"
  }'
```

Embedding example:

```bash
curl -X POST http://localhost:8000/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI makes it easy to build APIs with Python.",
    "model": "text-embedding-3-small"
  }'
```

Responses API example:

```bash
curl -X POST http://localhost:8000/responses \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Tell me a three sentence bedtime story about a unicorn.",
    "model": "gpt-4o-mini"
  }'
```

## Project structure

```
app/
  main.py              # FastAPI entrypoint
  api/routes.py        # API router definitions
  models/schema.py     # Pydantic request/response models
  services/openai_service.py  # OpenAI client wrapper
  config.py            # Environment-backed settings
requirements.txt
.env.example
README.md
```
