from agents.research_agent import ResearchAgent
from tools.tourism_db import initialize_tourism_db


def test_research_agent_fallback_when_ollama_unavailable(monkeypatch):
    initialize_tourism_db()
    agent = ResearchAgent(model="llama3.2")

    monkeypatch.setattr(agent, "_call_ollama", lambda prompt: None)

    result = agent.run("plan low cost hiking in ella", limit=4)

    assert result.used_fallback is True
    assert result.records
    assert "Research findings" in result.summary


def test_research_agent_uses_ollama_response(monkeypatch):
    initialize_tourism_db()
    agent = ResearchAgent(model="llama3.2")

    monkeypatch.setattr(agent, "_call_ollama", lambda prompt: "Verified summary")

    result = agent.run("best heritage places in kandy", limit=3)

    assert result.used_fallback is False
    assert result.model_used == "llama3.2"
    assert result.summary == "Verified summary"
