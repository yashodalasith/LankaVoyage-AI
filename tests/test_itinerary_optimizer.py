from importlib import import_module

itinerary_optimizer_module = import_module("tools.itinerary_optimizer")


def test_itinerary_optimizer_builds_daily_plan(monkeypatch):
    monkeypatch.setattr(itinerary_optimizer_module, "append_trace", lambda *args, **kwargs: None)

    research_data = [
        {
            "name": "Ravana Falls",
            "location": "Ella",
            "category": "nature",
            "estimated_cost_lkr": 0,
            "avg_duration_hours": 1.0,
            "description": "Waterfall",
        },
        {
            "name": "Nine Arches Bridge",
            "location": "Ella",
            "category": "scenic",
            "estimated_cost_lkr": 500,
            "avg_duration_hours": 1.5,
            "description": "Bridge",
        },
        {
            "name": "Ella Rock",
            "location": "Ella",
            "category": "hiking",
            "estimated_cost_lkr": 0,
            "avg_duration_hours": 5.0,
            "description": "Hike",
        },
    ]

    result = itinerary_optimizer_module.itinerary_optimizer(
        research_data=research_data,
        budget=80000,
        days=4,
        preferences={"origin": "Colombo", "destination": "Ella", "interests": ["hiking"]},
    )

    assert result["selected_attractions"]
    assert result["daily_plan"]
    assert result["cost_breakdown"]["total_lkr"] > 0
    assert result["feasibility"]["within_days"] is True
    assert result["decision_log"]
    assert len(result["daily_plan"]) == 4
    assert any(day.get("theme") == "light-exploration" for day in result["daily_plan"])
