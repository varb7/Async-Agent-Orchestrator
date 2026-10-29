# Async Agent Orchestrator

A small FastAPI service that demonstrates production-oriented async agent
orchestration: parallel fan-out/fan-in, bounded concurrency, deadlines,
retries, cancellation, and partial results.

The production reasoner is Hugging Face's `AsyncInferenceClient`. The default
`mock` provider is deterministic and keeps the demo and tests runnable without
network access or credentials.

## Run

```powershell
uv sync
uv run uvicorn async_orchestrator.api:app --reload
```

Open `http://127.0.0.1:8000/docs`, or submit a run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/runs -Method Post -ContentType application/json -Body '{"prompt":"Explain bounded concurrency."}'
```

## Use a Hugging Face model

Copy `.env.example` to `.env`, set `LLM_PROVIDER=huggingface`, and provide a
Hugging Face access token in `HF_TOKEN`. Export the variables before starting
the service; `.env` is intentionally not loaded automatically.

```powershell
$env:LLM_PROVIDER = "huggingface"
$env:HF_TOKEN = "hf_your_token"
uv run uvicorn async_orchestrator.api:app --reload
```

Run checks with `uv run pytest` and `uv run ruff check .`.
