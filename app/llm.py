import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "fake")


def model_name() -> str:
    if PROVIDER == "gemini":
        return os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    if PROVIDER == "claude":
        return os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")
    return "fake"


def build_prompt(text: str, max_words: int) -> str:
    return (
        f"Summarize the following text in at most {max_words} words. "
        f"Reply with the summary only.\n\n{text}"
    )


def build_analysis_prompt(text: str) -> str:
    return (
        "Analyze the following text. Reply with JSON only, no markdown, "
        'in exactly this shape: {"summary": "...", "key_points": ["..."], '
        '"sentiment": "positive" or "neutral" or "negative"}. '
        "Give at most 5 key_points.\n\n" + text
    )


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def call_llm(prompt: str, fake_reply: str = "placeholder summary") -> str:
    if PROVIDER == "gemini":
        from google import genai

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=model_name(), contents=prompt
        )
        return response.text

    if PROVIDER == "claude":
        from anthropic import Anthropic

        client = Anthropic()
        response = client.messages.create(
            model=model_name(),
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    return fake_reply


def summarize_text(text: str, max_words: int) -> str:
    return call_llm(build_prompt(text, max_words))


def analyze_text(text: str) -> str:
    fake = '{"summary": "placeholder", "key_points": ["a", "b"], "sentiment": "neutral"}'
    return strip_code_fences(call_llm(build_analysis_prompt(text), fake_reply=fake))