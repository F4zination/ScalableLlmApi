import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

# Load environment variables from a local .env file if present.
load_dotenv()


class Settings(BaseModel):
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")

    model_config = ConfigDict(extra="ignore")


def get_settings() -> Settings:
    """
    Build the settings object from environment variables.
    Environment defaults are provided to keep initialization lightweight.
    """
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
    )


settings = get_settings()
