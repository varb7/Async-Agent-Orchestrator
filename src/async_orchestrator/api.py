"""FastAPI service boundary."""

from __future__ import annotations

from fastapi import FastAPI

from .agents import make_agents
from .models import RunRequest, RunResponse
from .orchestrator import Orchestrator
from .providers import Reasoner, build_reasoner
from .settings import Settings


def build_orchestrator(settings: Settings | None = None) -> tuple[Orchestrator, Reasoner]:
    settings = settings or Settings.from_env()
    return (
        Orchestrator(
            concurrency=settings.concurrency,
            timeout_seconds=settings.timeout_seconds,
            retries=settings.retries,
        ),
        build_reasoner(settings),
    )


def create_app(service: tuple[Orchestrator, Reasoner] | None = None) -> FastAPI:
    app = FastAPI(title="Async Agent Orchestrator")
    orchestrator, reasoner = service or build_orchestrator()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/runs", response_model=RunResponse)
    async def run(request: RunRequest) -> RunResponse:
        agents = make_agents(request.agents, reasoner)
        return RunResponse(results=await orchestrator.run(request.prompt, agents))

    return app


app = create_app()
