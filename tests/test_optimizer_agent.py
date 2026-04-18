from agents.optimizer_agent import OptimizerAgent
from agents.research_agent import ResearchAgentResult
from importlib import import_module

itinerary_optimizer_module = import_module("tools.itinerary_optimizer")
trace_logger_module = import_module("tools.trace_logger")


def test_optimizer_agent_uses_fallback_summary(monkeypatch):
    monkeypatch.setattr(itinerary_optimizer_module, "append_trace", lambda *args, **kwargs: None)
    monkeypatch.setattr(trace_logger_module, "append_trace", lambda *args, **kwargs: None)

    research_result = ResearchAgentResult(
        query="Plan a 4-day budget trip to Ella from Colombo under 80000 LKR",
        records=[
            {
                "name": "Ravana Falls",
                "location": "Ella",
                "district": "Badulla",
                "category": "nature",
                "estimated_cost_lkr": 0,
                "avg_duration_hours": 1.0,
                "description": "Waterfall",
            }
        ],
        summary="Verified research summary",
        model_used="llama3.2",
        used_fallback=False,
    )

    agent = OptimizerAgent(model="llama3.2")
    monkeypatch.setattr(agent, "_call_ollama", lambda prompt: None)

    result = agent.run(
        user_query="Plan a 4-day budget trip to Ella from Colombo under 80000 LKR",
        research_result=research_result,
    )

    assert result.used_fallback is True
    assert result.model_used == "fallback"
    assert "Optimizer summary" in result.summary
    assert result.optimized_plan["decision_log"]


def test_optimizer_agent_uses_ollama_response(monkeypatch):
    monkeypatch.setattr(itinerary_optimizer_module, "append_trace", lambda *args, **kwargs: None)
    monkeypatch.setattr(trace_logger_module, "append_trace", lambda *args, **kwargs: None)

    research_result = ResearchAgentResult(
        query="Best heritage trip to Kandy in 2 days",
        records=[
            {
                "name": "Temple of the Tooth",
                "location": "Kandy",
                "district": "Kandy",
                "category": "heritage",
                "estimated_cost_lkr": 2500,
                "avg_duration_hours": 2.0,
                "description": "Temple",
            }
        ],
        summary="Verified research summary",
        model_used="llama3.2",
        used_fallback=False,
    )

    agent = OptimizerAgent(model="llama3.2")
    monkeypatch.setattr(agent, "_call_ollama", lambda prompt: "Optimized itinerary summary")

    result = agent.run(user_query="Best heritage trip to Kandy in 2 days", research_result=research_result)

    assert result.used_fallback is False
    assert result.model_used == "llama3.2"
    assert result.summary == "Optimized itinerary summary"


def test_optimizer_agent_parses_origin_destination_with_extra_phrases():
    agent = OptimizerAgent(model="llama3.2")
    preferences = agent._parse_preferences(
        "Plan a 4-day budget trip to Ella from Colombo for a couple, max 80000 LKR, focus on nature and hiking"
    )

    assert preferences["origin"] == "Colombo"
    assert preferences["destination"] == "Ella"
