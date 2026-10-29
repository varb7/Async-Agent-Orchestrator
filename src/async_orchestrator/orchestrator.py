"""Async fan-out/fan-in with bounded concurrency and partial failures."""

from __future__ import annotations

import asyncio
from time import perf_counter

from .agents import Agent
from .models import AgentResult


class Orchestrator:
    def __init__(self, *, concurrency: int, timeout_seconds: float, retries: int) -> None:
        self._semaphore = asyncio.Semaphore(concurrency)
        self._timeout_seconds = timeout_seconds
        self._retries = retries

    async def run(self, prompt: str, agents: list[Agent]) -> list[AgentResult]:
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(self._run_one(agent, prompt)) for agent in agents]
        return [task.result() for task in tasks]

    async def _run_one(self, agent: Agent, prompt: str) -> AgentResult:
        started = perf_counter()
        for attempt in range(1, self._retries + 2):
            try:
                async with asyncio.timeout(self._timeout_seconds):
                    async with self._semaphore:
                        output = await agent.run(prompt)
                return AgentResult(
                    agent=agent.name,
                    status="ok",
                    output=output,
                    duration_ms=_elapsed_ms(started),
                    attempts=attempt,
                )
            except asyncio.CancelledError:
                raise
            except TimeoutError:
                if attempt > self._retries:
                    return AgentResult(
                        agent=agent.name,
                        status="timed_out",
                        error="agent deadline exceeded",
                        duration_ms=_elapsed_ms(started),
                        attempts=attempt,
                    )
            except (ConnectionError, OSError) as error:
                if attempt > self._retries:
                    return _failure(agent.name, error, started, attempt)
            except Exception as error:
                return _failure(agent.name, error, started, attempt)
            await asyncio.sleep(0.1 * 2 ** (attempt - 1))
        raise AssertionError("unreachable")


def _failure(name: str, error: Exception, started: float, attempts: int) -> AgentResult:
    return AgentResult(
        agent=name,
        status="failed",
        error=f"{type(error).__name__}: {error}",
        duration_ms=_elapsed_ms(started),
        attempts=attempts,
    )


def _elapsed_ms(started: float) -> int:
    return round((perf_counter() - started) * 1_000)
