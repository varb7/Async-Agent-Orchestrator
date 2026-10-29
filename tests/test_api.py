from fastapi.testclient import TestClient

from async_agent_orchestrator.api import create_app
from async_agent_orchestrator.orchestrator import Orchestrator
from async_agent_orchestrator.providers import MockReasoner


def test_health_and_run() -> None:
    app = create_app((Orchestrator(concurrency=2, timeout_seconds=1, retries=0), MockReasoner()))
    client = TestClient(app)

    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/runs", json={"prompt": "Explain a semaphore.", "agents": ["analyst"]})

    assert response.status_code == 200
    assert response.json()["results"][0]["status"] == "ok"
