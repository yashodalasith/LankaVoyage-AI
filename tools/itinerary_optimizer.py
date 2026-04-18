from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from tools.tourism_db import DEFAULT_DB_PATH, tourism_db_query
from tools.trace_logger import append_trace


@dataclass
class OptimizationSelection:
    name: str
    location: str
    category: str
    estimated_cost_lkr: int
    avg_duration_hours: float
    description: str


def itinerary_optimizer(
    research_data: List[Dict[str, Any]],
    budget: int,
    days: int,
    preferences: Dict[str, Any],
) -> Dict[str, Any]:
    """Optimize a trip plan using greedy selection and simple budget allocation.

    The function prioritizes lower-cost attractions first, keeps the plan within the
    requested day count, and returns a structured optimization trace for visibility.
    """
    append_trace(
        "optimizer_input",
        {
            "budget": budget,
            "days": days,
            "preferences": preferences,
            "records": research_data,
        },
    )

    sorted_places = sorted(
        research_data,
        key=lambda row: (int(row.get("estimated_cost_lkr", 0)), float(row.get("avg_duration_hours", 0.0))),
    )

    selected_places: List[OptimizationSelection] = []
    decision_log: List[str] = []
    attraction_budget = _allocate_attraction_budget(budget, days)
    running_cost = 0
    running_hours = 0.0

    for place in sorted_places:
        place_cost = int(place.get("estimated_cost_lkr", 0))
        place_hours = float(place.get("avg_duration_hours", 0.0))

        if len(selected_places) >= max(1, days * 2):
            decision_log.append("Stopped selection after reaching the attraction count cap for the requested trip length.")
            break

        if running_cost + place_cost > attraction_budget:
            decision_log.append(
                f"Skipped {place.get('name')} because adding {place_cost} LKR would exceed the attraction budget cap of {attraction_budget} LKR."
            )
            continue

        selected_places.append(
            OptimizationSelection(
                name=str(place.get("name", "Unknown")),
                location=str(place.get("location", "Unknown")),
                category=str(place.get("category", "general")),
                estimated_cost_lkr=place_cost,
                avg_duration_hours=place_hours,
                description=str(place.get("description", "")),
            )
        )
        running_cost += place_cost
        running_hours += place_hours
        decision_log.append(
            f"Selected {place.get('name')} because it fits the budget and adds {place_hours:.1f} hours of activity value."
        )

    if not selected_places and research_data:
        first_place = research_data[0]
        selected_places.append(
            OptimizationSelection(
                name=str(first_place.get("name", "Unknown")),
                location=str(first_place.get("location", "Unknown")),
                category=str(first_place.get("category", "general")),
                estimated_cost_lkr=int(first_place.get("estimated_cost_lkr", 0)),
                avg_duration_hours=float(first_place.get("avg_duration_hours", 0.0)),
                description=str(first_place.get("description", "")),
            )
        )
        decision_log.append("Budget selection was empty, so the top verified attraction was used as a minimum viable plan.")

    transport_cost = _estimate_transport_cost(preferences, days)
    accommodation_cost = _estimate_accommodation_cost(preferences, days)
    food_cost = _estimate_food_cost(days)
    total_attraction_cost = sum(place.estimated_cost_lkr for place in selected_places)
    total_cost = total_attraction_cost + transport_cost + accommodation_cost + food_cost

    day_plans = _distribute_places_across_days(selected_places, days)
    feasibility = {
        "within_budget": total_cost <= budget,
        "within_days": len(day_plans) <= days,
        "days_requested": days,
        "days_planned": len(day_plans),
    }

    result = {
        "trip_summary": {
            "origin": preferences.get("origin", "Unknown"),
            "destination": preferences.get("destination", "Unknown"),
            "budget_lkr": budget,
            "days": days,
            "interests": preferences.get("interests", []),
        },
        "selected_attractions": [place.__dict__ for place in selected_places],
        "daily_plan": day_plans,
        "cost_breakdown": {
            "attractions_lkr": total_attraction_cost,
            "transport_lkr": transport_cost,
            "accommodation_lkr": accommodation_cost,
            "food_lkr": food_cost,
            "total_lkr": total_cost,
            "budget_lkr": budget,
        },
        "feasibility": feasibility,
        "decision_log": decision_log,
        "reasoning_summary": _build_reasoning_summary(selected_places, total_cost, budget, days),
        "source_database": str(DEFAULT_DB_PATH),
    }

    append_trace("optimizer_output", result)
    return result


def _allocate_attraction_budget(budget: int, days: int) -> int:
    daily_share = max(1, budget // max(days, 1))
    return int(daily_share * max(1, days) * 0.35)


def _estimate_transport_cost(preferences: Dict[str, Any], days: int) -> int:
    origin = str(preferences.get("origin", "")).lower()
    destination = str(preferences.get("destination", "")).lower()

    candidates = tourism_db_query(
        f"SELECT avg_fare_lkr FROM transport WHERE LOWER(from_city) LIKE '%{origin}%' AND LOWER(to_city) LIKE '%{destination}%'",
        limit=5,
    )
    if candidates and "avg_fare_lkr" in candidates[0]:
        return int(candidates[0]["avg_fare_lkr"])

    return 1200 if days <= 2 else 2200


def _estimate_accommodation_cost(preferences: Dict[str, Any], days: int) -> int:
    destination = str(preferences.get("destination", "")).lower()
    candidates = tourism_db_query(
        f"SELECT min_cost_lkr, max_cost_lkr FROM costs WHERE LOWER(item_type) LIKE '%accommodation%' AND (LOWER(location) LIKE '%{destination}%' OR LOWER(location) = 'sri lanka')",
        limit=5,
    )
    if candidates and "min_cost_lkr" in candidates[0] and "max_cost_lkr" in candidates[0]:
        avg_per_night = (int(candidates[0]["min_cost_lkr"]) + int(candidates[0]["max_cost_lkr"])) // 2
        return avg_per_night * max(days, 1)

    return 9000 * max(days, 1)


def _estimate_food_cost(days: int) -> int:
    return 2500 * max(days, 1)


def _distribute_places_across_days(
    selected_places: List[OptimizationSelection],
    days: int,
) -> List[Dict[str, Any]]:
    if not selected_places:
        return []

    total_days = max(1, days)
    buckets: List[List[OptimizationSelection]] = [[] for _ in range(total_days)]
    for index, place in enumerate(selected_places):
        buckets[index % total_days].append(place)

    plan: List[Dict[str, Any]] = []
    for day_index, bucket in enumerate(buckets, start=1):
        if not bucket:
            continue
        plan.append(
            {
                "day": day_index,
                "theme": bucket[0].category,
                "stops": [
                    {
                        "name": place.name,
                        "location": place.location,
                        "category": place.category,
                        "estimated_cost_lkr": place.estimated_cost_lkr,
                        "avg_duration_hours": place.avg_duration_hours,
                    }
                    for place in bucket
                ],
                "day_cost_lkr": sum(place.estimated_cost_lkr for place in bucket),
                "day_duration_hours": round(sum(place.avg_duration_hours for place in bucket), 1),
            }
        )
    return plan


def _build_reasoning_summary(
    selected_places: List[OptimizationSelection],
    total_cost: int,
    budget: int,
    days: int,
) -> str:
    selected_names = ", ".join(place.name for place in selected_places[:5]) or "no attractions"
    status = "within budget" if total_cost <= budget else "over budget"
    return (
        f"Greedy selection prioritized the verified lower-cost attractions first, then grouped them across {days} day(s). "
        f"Selected places: {selected_names}. Estimated total cost is {total_cost} LKR against the target budget of {budget} LKR, so the plan is {status}."
    )
