import asyncio

from async_agent_orchestrator.agents import Agent
from async_agent_orchestrator.orchestrator import Orchestrator


class SlowReasoner:
    def __init__(self) -> None:
        self.in_flight = 0
        self.peak = 0

    async def complete(self, system_prompt: str, prompt: str) -> str:
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        await asyncio.sleep(0.01)
        self.in_flight -= 1
        return prompt


async def test_orchestrator_bounds_concurrency() -> None:
    reasoner = SlowReasoner()
    agents = [Agent(str(index), "test", reasoner) for index in range(5)]

    results = await Orchestrator(concurrency=2, timeout_seconds=1, retries=0).run("hello", agents)

    assert reasoner.peak == 2
    assert [result.status for result in results] == ["ok"] * 5


async def test_orchestrator_returns_timeout_as_partial_result() -> None:
    class NeverFinishes:
        async def complete(self, system_prompt: str, prompt: str) -> str:
            await asyncio.sleep(1)
            return prompt

    result = await Orchestrator(concurrency=1, timeout_seconds=0.01, retries=0).run(
        "hello", [Agent("slow", "test", NeverFinishes())]
    )

    assert result[0].status == "timed_out"
