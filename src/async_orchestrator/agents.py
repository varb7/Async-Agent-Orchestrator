"""Small role-specific wrappers around a shared LLM reasoner."""

from __future__ import annotations

from dataclasses import dataclass

from .providers import Reasoner


INSTRUCTIONS = {
    "researcher": "Research the prompt and identify relevant facts and assumptions.",
    "analyst": "Analyse the prompt, trade-offs, and a practical recommendation.",
    "reviewer": "Review the prompt for risks, gaps, and important caveats.",
}


@dataclass(frozen=True, slots=True)
class Agent:
    name: str
    instruction: str
    reasoner: Reasoner

    async def run(self, prompt: str) -> str:
        return await self.reasoner.complete(self.instruction, prompt)


def make_agents(names: list[str], reasoner: Reasoner) -> list[Agent]:
    return [Agent(name, INSTRUCTIONS[name], reasoner) for name in names]
