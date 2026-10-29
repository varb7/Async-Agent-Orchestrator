"""Environment-backed runtime settings."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    provider: str = "mock"
    hf_token: str | None = None
    hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    hf_provider: str = "auto"
    concurrency: int = 3
    timeout_seconds: float = 30.0
    retries: int = 1

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            provider=getenv("LLM_PROVIDER", "mock"),
            hf_token=getenv("HF_TOKEN"),
            hf_model=getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
            hf_provider=getenv("HF_PROVIDER", "auto"),
            concurrency=int(getenv("AGENT_CONCURRENCY", "3")),
            timeout_seconds=float(getenv("AGENT_TIMEOUT_SECONDS", "30")),
            retries=int(getenv("AGENT_RETRIES", "1")),
        )
