"""LLM reasoners. The orchestrator depends only on the protocol below."""

from __future__ import annotations

import asyncio
from typing import Protocol

from huggingface_hub import AsyncInferenceClient

from .settings import Settings


class Reasoner(Protocol):
    async def complete(self, system_prompt: str, prompt: str) -> str: ...


class MockReasoner:
    """Offline reasoner used by the demo and test suite."""

    async def complete(self, system_prompt: str, prompt: str) -> str:
        await asyncio.sleep(0.01)
        return f"{system_prompt.split('.')[0]}: {prompt}"


class HuggingFaceReasoner:
    def __init__(self, settings: Settings) -> None:
        if not settings.hf_token:
            raise ValueError("HF_TOKEN is required when LLM_PROVIDER=huggingface")
        self._client = AsyncInferenceClient(
            model=settings.hf_model,
            provider=settings.hf_provider,
            token=settings.hf_token,
            timeout=settings.timeout_seconds,
        )

    async def complete(self, system_prompt: str, prompt: str) -> str:
        response = await self._client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=512,
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Hugging Face returned an empty completion")
        return content


def build_reasoner(settings: Settings) -> Reasoner:
    if settings.provider == "mock":
        return MockReasoner()
    if settings.provider == "huggingface":
        return HuggingFaceReasoner(settings)
    raise ValueError("LLM_PROVIDER must be 'mock' or 'huggingface'")
