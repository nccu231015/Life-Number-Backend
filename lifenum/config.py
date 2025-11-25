from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(default=None, alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")  
    project_locale: str = Field(default="zh-TW", alias="PROJECT_LOCALE")

    class Config:
        populate_by_name = True


def load_settings() -> Settings:
    load_dotenv(override=False)
    data = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "PROJECT_LOCALE": os.getenv("PROJECT_LOCALE", "zh-TW"),
    }
    return Settings.model_validate(data)
