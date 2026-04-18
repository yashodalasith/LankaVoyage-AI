from pathlib import Path

from tools.report_generator import report_generator


def test_report_generator_writes_markdown(tmp_path):
    plan = {
        "trip_summary": {
            "origin": "Colombo",
            "destination": "Ella",
            "days": 4,
            "budget_lkr": 80000,
            "interests": ["nature", "hiking"],
        },
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
        "personalized_notes": ["Start hikes early."],
    }

    output_name = "test_itinerary_output.md"
    output_path = Path(report_generator(plan, filename=output_name))

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Personalized Itinerary" in content
    assert "Ravana Falls" in content
    output_path.unlink()
