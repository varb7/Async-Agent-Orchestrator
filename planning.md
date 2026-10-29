# Async Agentic Orchestrator — Plan

## Goal

Build a small, production-shaped reference service that shows how asynchronous
Python coordinates multiple AI agents safely: concurrent work, bounded
parallelism, timeouts, retries, cancellation, structured results, and
observability.

The project should teach real async patterns rather than hide them behind a
large orchestration framework.

## Chosen stack

| Concern | Choice | Why |
| --- | --- | --- |
| Language/runtime | Python 3.12+ | First-class `async`/`await`, `TaskGroup`, and a widely used AI ecosystem. |
| Concurrency | Standard-library `asyncio` | Makes the async mechanics visible; no workflow engine is needed for the initial scope. |
| HTTP API | FastAPI + Uvicorn | Async-native, typed request validation, automatic OpenAPI documentation, and production adoption. |
| Data validation | Pydantic (via FastAPI) | Defines clear task, agent, and result contracts. |
| HTTP client | `httpx` | Async client with connection pooling and timeout controls. |
| LLM provider | OpenAI Python SDK behind a small adapter | Supports real model calls while keeping the orchestrator testable and provider-replaceable. |
| Configuration | `pydantic-settings` | Typed environment-based configuration; secrets remain outside source control. |
| Logging/metrics | Standard `logging` + OpenTelemetry | Structured operational signals without committing to a hosted vendor. |
| Tests | `pytest` + `pytest-asyncio` | Direct async unit and API tests. |
| Packaging/tooling | `uv` + Ruff | Fast, simple dependency management and formatting/linting. |
| Deployment | Docker | A portable service unit; add an orchestrator platform only when deployment requires it. |

### Explicitly deferred

- **LangGraph, Temporal, Celery, or Airflow:** valuable for durable,
  long-running, or scheduled workflows, but obscure the core async lesson in
  version one.
- **A database:** start with in-memory request state. Add PostgreSQL when
  runs, audit history, or cross-instance coordination must persist.
- **A message broker:** add Redis/RabbitMQ only when work must outlive an HTTP
  request or throughput needs queue-based backpressure.
- **Multiple model providers:** retain an adapter seam, but implement one
  provider first.

## Initial architecture

```text
Client
  |
  v
FastAPI endpoint
  |
  v
Orchestrator
  |- validates and decomposes the request
  |- starts independent agents in an asyncio.TaskGroup
  |- enforces a shared concurrency Semaphore
  |- applies per-agent timeouts and retry policy
  |- cancels sibling work on fatal failure
  v
Result aggregator --> structured response + logs/traces
  |
  v
LLM adapter / mocked agent implementations
```

Core domain types:

- `AgentTask`: work item, input, deadline, and correlation ID.
- `AgentResult`: status, output, timing, retry count, and error details.
- `Agent`: async protocol implemented by LLM-backed and deterministic demo agents.
- `Orchestrator`: owns task lifecycle, concurrency limits, and aggregation.

## Async behaviours to demonstrate

1. **Parallel fan-out/fan-in:** use `asyncio.TaskGroup` for independent
   research, analysis, and review agents.
2. **Bounded concurrency:** use `asyncio.Semaphore` so a large request cannot
   exhaust provider or server resources.
3. **Deadlines:** wrap external calls with `asyncio.timeout`; propagate the
   request deadline to child work.
4. **Retries:** retry only transient provider/network failures with capped
   exponential backoff and jitter.
5. **Cancellation:** propagate client shutdown or fatal agent failure through
   `CancelledError`; always release resources in `finally` blocks.
6. **Partial failures:** return successful agent outputs alongside explicit
   failed/timed-out results where the workflow permits it.
7. **Backpressure:** reject or queue work once a configurable in-flight limit
   is reached.
8. **Observability:** correlation IDs, task duration, retry count, and outcome
   appear in logs and traces.

## Delivery phases

### Phase 1 — Runnable async core

- Create the Python project and development tooling.
- Implement domain models, the agent protocol, deterministic demo agents, and
  `Orchestrator.run()`.
- Demonstrate fan-out/fan-in, semaphore limits, timeouts, cancellation, and
  partial results.
- Add focused async tests.

**Done when:** a CLI/demo can run several simulated agents concurrently and
prints structured results with timing.

### Phase 2 — Service boundary

- Add `POST /runs` to submit a task and `GET /health`.
- Validate inputs and expose clear error responses.
- Add request IDs, structured logs, and configuration via environment.

**Done when:** the service is runnable locally and its OpenAPI page can drive
a concurrent orchestration request.

### Phase 3 — Real model integration

- Add the OpenAI adapter and a mock adapter selected by configuration.
- Define safe provider timeouts, retryable errors, and token/cost metadata.
- Keep tests offline by using the mock adapter.

**Done when:** an environment-configured deployment can execute the same
workflow against a real model provider.

### Phase 4 — Production hardening

- Add OpenTelemetry tracing and metrics.
- Add Docker, CI, dependency/security checks, and load tests.
- Document operational limits and graceful shutdown.

**Done when:** the service has reproducible builds, health checks, telemetry,
and documented deployment settings.

### Phase 5 — Durable workflows (only if needed)

- Add PostgreSQL for run history and idempotency records.
- Introduce a queue or workflow engine if runs must survive restarts, wait for
  external events, or span minutes/hours.

**Done when:** durability requirements exist and are verified with restart and
duplicate-delivery tests.

## Initial project layout

```text
src/async_orchestrator/
  api.py             # FastAPI routes
  orchestrator.py    # Task lifecycle and concurrency policy
  agents.py          # Agent protocol and implementations
  models.py          # Pydantic contracts
  providers.py       # LLM adapter boundary
  settings.py        # Environment configuration
tests/
  test_orchestrator.py
  test_api.py
```

## Decisions to revisit

- Replace the in-process limit with a distributed queue when multiple replicas
  need shared backpressure.
- Add persistence only for a stated retention, replay, or audit requirement.
- Introduce LangGraph or Temporal only when workflows need graphs, human
  approval, resumability, or durable execution beyond what `asyncio` provides.

## Next implementation step

Set up the Phase 1 Python package with deterministic agents and tests before
adding an API or connecting a model provider.
