from typing import Literal

from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    text: str = Field(min_length=20, max_length=5000)
    max_words: int = Field(default=50, ge=10, le=200)


class SummaryResponse(BaseModel):
    summary: str
    model: str


class AnalysisResult(BaseModel):
    summary: str
    key_points: list[str] = Field(max_length=5)
    sentiment: Literal["positive", "neutral", "negative"]
