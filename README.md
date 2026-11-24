# llm-api-starter

A small FastAPI service that puts an LLM behind validated HTTP endpoints. It summarises text, returns structured analysis as validated JSON, and fails cleanly when the model call goes wrong. The model provider (Gemini, Claude, or an offline fake) is switched with one environment variable.

Built as a learning project to practise the pieces a real LLM-backed API needs: request validation, structured output, secrets handling, error handling and tests that never touch a paid API.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok"}`. |
| POST | `/summarize` | Summarises `text` in roughly `max_words` words. |
| POST | `/analyze` | Returns a summary, up to 5 key points and a sentiment, as validated JSON. |

Interactive docs are served at `http://127.0.0.1:8000/docs` once the app is running.

### `POST /summarize`

Request (`text` must be 20 to 5000 characters, `max_words` 10 to 200, default 50):

```json
{
  "text": "FastAPI is a modern Python web framework. It uses type hints to validate requests automatically. It also generates interactive documentation. Many teams use it to serve machine learning models.",
  "max_words": 50
}
```

Example response (the wording varies between runs):

```json
{
  "summary": "FastAPI is a modern Python web framework that utilizes type hints for automatic request validation and interactive documentation generation. It is widely favored for deploying machine learning models.",
  "model": "gemini-3.1-flash-lite"
}
```

### `POST /analyze`

Takes the same request body. Example response:

```json
{
  "summary": "The new phone offers an excellent display and battery life, but is hampered by a weak low-light camera and a high price point, despite receiving good customer support.",
  "key_points": [
    "Stunning display",
    "Two-day battery life",
    "Poor low-light camera performance",
    "Higher price compared to competitors",
    "Helpful customer support"
  ],
  "sentiment": "neutral"
}
```

`sentiment` is always one of `positive`, `neutral` or `negative`. The model's reply is parsed and validated against a Pydantic schema before it is returned.

### Errors

| Status | When |
|---|---|
| 422 | The request body breaks a validation rule (for example, text shorter than 20 characters). |
| 502 | The LLM call failed, returned an empty answer, or returned JSON that does not match the schema. |

Error responses to the client are deliberately generic. The full traceback is written to the server log.

## Setup

Requires Python 3.10 or newer.

```bash
git clone https://github.com/naashit10/llm-api-starter.git
cd llm-api-starter
python -m venv venv
source venv/Scripts/activate      # Git Bash on Windows
# source venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
```

Copy the example settings file and fill it in:

```bash
cp .env.example .env
```

| Variable | Meaning |
|---|---|
| `LLM_PROVIDER` | `fake` (default, no key needed), `gemini` or `claude`. |
| `GEMINI_API_KEY` | Needed when `LLM_PROVIDER=gemini`. |
| `GEMINI_MODEL` | Gemini model name, for example `gemini-3.1-flash-lite`. |
| `ANTHROPIC_API_KEY` | Needed when `LLM_PROVIDER=claude`. |
| `CLAUDE_MODEL` | Claude model name. |

`.env` is listed in `.gitignore` and must never be committed. If `LLM_PROVIDER` is missing the app runs in `fake` mode, so it starts and the tests pass on a fresh clone with no keys.

Model names change over time. Check the provider's documentation for current ones.

## Run

```bash
uvicorn app.main:app --reload
```

`--reload` watches Python files only. After editing `.env`, stop the server (Ctrl+C) and start it again.

Quick check with curl:

```bash
curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "FastAPI is a modern Python framework for building APIs quickly.", "max_words": 20}'
```

## Tests

```bash
pytest -v
```

The tests force `LLM_PROVIDER=fake`, so they are free, fast and need no network. They cover:

- the health check;
- a normal `/summarize` call in fake mode;
- rejection of too-short input (422);
- `/analyze` returning a valid structure;
- the 502 path, using `monkeypatch` to make the LLM call raise an error.

## Project layout

```
app/
  main.py      routes, error handling, logging
  schemas.py   Pydantic request and response models
  llm.py       provider switch (fake / gemini / claude) and prompt building
tests/
  test_api.py  pytest suite
pytest.ini     lets pytest import the app package
.env.example   template for local settings
```

## Design notes

- **One file knows the provider.** Only `app/llm.py` imports a provider SDK, and only the chosen provider's SDK is imported. Changing provider is a change to `.env`, not to the routes.
- **Validate model output, do not trust it.** `/analyze` asks for JSON, strips any markdown fences, then validates the result with Pydantic (`Literal` for sentiment, a cap on the number of key points). Anything that does not match becomes a 502.
- **Tests never call a real model.** Fake mode covers the happy path, and `monkeypatch` simulates failure.

## Limitations and next steps

- The `claude` provider path is written but has not been exercised end to end yet. The Gemini path has been run against the real API.
- `max_words` is passed to the model as an instruction. Models do not count words exactly, so summaries can run slightly over.
- `/analyze` reuses the summary request model, so it accepts `max_words` but ignores it.
- Tool calling is not implemented yet.
- No authentication or rate limiting. This is a local learning project, not a production service.
