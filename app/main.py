import logging
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from app.llm import summarize_text, analyze_text, model_name
from app.schemas import AnalysisResult, SummaryRequest, SummaryResponse

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/summarize", response_model=SummaryResponse)
def summarize(request: SummaryRequest):
    try:
        summary = summarize_text(request.text, request.max_words)
    except Exception as e:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=502, detail="The LLM call failed") from e

    if not summary or not summary.strip():
        raise HTTPException(status_code=502, detail="The LLM returned an empty response")

    return SummaryResponse(summary=summary, model=model_name())


@app.post("/analyze", response_model=AnalysisResult)
def analyze(request: SummaryRequest):
    try:
        raw = analyze_text(request.text)
    except Exception as e:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=502, detail="The LLM call failed") from e

    try:
        return AnalysisResult.model_validate_json(raw)
    except ValidationError as e:
        logger.error("LLM returned invalid structure: %s", raw)
        raise HTTPException(
            status_code=502, detail="The LLM returned an invalid structure"
        ) from e