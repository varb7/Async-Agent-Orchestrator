"""Public request and response contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12_000)
    agents: list[Literal["researcher", "analyst", "reviewer"]] = Field(
        default_factory=lambda: ["researcher", "analyst", "reviewer"]
    )


class AgentResult(BaseModel):
    agent: str
    status: Literal["ok", "failed", "timed_out"]
    output: str | None = None
    error: str | None = None
    duration_ms: int
    attempts: int


class RunResponse(BaseModel):
    results: list[AgentResult]
