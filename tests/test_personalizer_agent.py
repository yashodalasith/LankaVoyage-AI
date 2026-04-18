from pathlib import Path

from agents.optimizer_agent import OptimizerAgentResult
from agents.personalizer_agent import PersonalizerAgent


def _sample_optimizer_result() -> OptimizerAgentResult:
    return OptimizerAgentResult(
        query="Plan a 4-day budget trip to Ella from Colombo under 80000 LKR",
        preferences={
            "budget_lkr": 80000,
            "days": 4,
            "origin": "Colombo",
            "destination": "Ella",
            "interests": ["nature", "hiking"],
        },
        optimized_plan={
            "trip_summary": {
                "origin": "Colombo",
                "destination": "Ella",
                "budget_lkr": 80000,
                "days": 4,
                "interests": ["nature", "hiking"],
            },
            "selected_attractions": [
                {
                    "name": "Ravana Falls",
                    "location": "Ella",
                    "category": "nature",
                    "estimated_cost_lkr": 0,
                    "avg_duration_hours": 1.0,
                    "description": "Waterfall",
                }
            ],
            "daily_plan": [
                {
                    "day": 1,
                    "theme": "nature",
                    "stops": [
                        {
                            "name": "Ravana Falls",
                            "location": "Ella",
                            "category": "nature",
                            "estimated_cost_lkr": 0,
                            "avg_duration_hours": 1.0,
                        }
                    ],
                    "day_cost_lkr": 0,
                    "day_duration_hours": 1.0,
                }
            ],
            "cost_breakdown": {
                "attractions_lkr": 0,
                "transport_lkr": 1600,
                "accommodation_lkr": 36000,
                "food_lkr": 10000,
                "total_lkr": 47600,
                "budget_lkr": 80000,
            },
            "feasibility": {
                "within_budget": True,
                "within_days": True,
                "days_requested": 4,
                "days_planned": 1,
            },
            "decision_log": ["Selected Ravana Falls"],
            "reasoning_summary": "Within budget.",
            "source_database": "data/sri_lanka_tourism.db",
        },
        summary="Optimizer summary",
        model_used="llama3.2",
        used_fallback=False,
    )


def test_personalizer_agent_fallback(monkeypatch):
    agent = PersonalizerAgent(model="llama3.2")
    monkeypatch.setattr(agent, "_call_ollama", lambda prompt: None)

    result = agent.run(
        user_query="Plan a 4-day budget trip to Ella from Colombo under 80000 LKR",
        optimizer_result=_sample_optimizer_result(),
        output_filename="test_personalizer_fallback.md",
    )

    assert result.used_fallback is True
    assert result.model_used == "fallback"
    assert result.report_path.endswith("test_personalizer_fallback.md")
    path = Path(result.report_path)
    if path.exists():
        path.unlink()


def test_personalizer_agent_llm_response(monkeypatch):
    agent = PersonalizerAgent(model="llama3.2")
    monkeypatch.setattr(agent, "_call_ollama", lambda prompt: "Personalized final summary")

    result = agent.run(
        user_query="Plan a 4-day budget trip to Ella from Colombo under 80000 LKR for a couple",
        optimizer_result=_sample_optimizer_result(),
        output_filename="test_personalizer_llm.md",
    )

    assert result.used_fallback is False
    assert result.model_used == "llama3.2"
    assert result.personalized_summary == "Personalized final summary"
    path = Path(result.report_path)
    if path.exists():
        path.unlink()
