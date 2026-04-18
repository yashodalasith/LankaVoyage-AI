from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from tools.observability import log_event

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_FILE = WORKSPACE_ROOT / "itinerary.md"


def report_generator(final_plan: Dict[str, Any], filename: str = "itinerary.md") -> str:
    """Generate a polished markdown itinerary report and return the output path.

    Args:
        final_plan: Structured itinerary plan prepared by the personalizer agent.
        filename: Output markdown filename.

    Returns:
        Absolute path to the generated markdown file.
    """
    output_path = WORKSPACE_ROOT / filename
    log_event("tool-report", "report_generation_started", {"output": str(output_path)})

    trip_summary = final_plan.get("trip_summary", {})
    daily_plan: List[Dict[str, Any]] = final_plan.get("daily_plan", [])
    cost_breakdown = final_plan.get("cost_breakdown", {})
    personalized_notes: List[str] = final_plan.get("personalized_notes", [])

    lines: List[str] = []
    lines.append("# LankaVoyage AI - Personalized Itinerary")
    lines.append("")
    lines.append("## Trip Snapshot")
    lines.append(f"- Origin: {trip_summary.get('origin', 'Unknown')}")
    lines.append(f"- Destination: {trip_summary.get('destination', 'Unknown')}")
    lines.append(f"- Duration: {trip_summary.get('days', 'Unknown')} day(s)")
    lines.append(f"- Budget: {trip_summary.get('budget_lkr', 'Unknown')} LKR")
    interests = trip_summary.get("interests", [])
    lines.append(f"- Interests: {', '.join(interests) if interests else 'General exploration'}")
    lines.append("")

    lines.append("## Daily Itinerary")
    if not daily_plan:
        lines.append("- No day-by-day activities were generated.")
    for day in daily_plan:
        lines.append("")
        lines.append(f"### Day {day.get('day', '?')} - {day.get('theme', 'Experience')}")
        for stop in day.get("stops", []):
            lines.append(
                f"- {stop.get('name', 'Unknown stop')} ({stop.get('location', 'Unknown location')}) "
                f"| {stop.get('category', 'activity')} | "
                f"{stop.get('estimated_cost_lkr', 0)} LKR | {stop.get('avg_duration_hours', 0)} hrs"
            )
        lines.append(f"- Day cost estimate: {day.get('day_cost_lkr', 0)} LKR")
        lines.append(f"- Day duration estimate: {day.get('day_duration_hours', 0)} hours")

    lines.append("")
    lines.append("## Cost Overview")
    lines.append(f"- Attractions: {cost_breakdown.get('attractions_lkr', 0)} LKR")
    lines.append(f"- Transport: {cost_breakdown.get('transport_lkr', 0)} LKR")
    lines.append(f"- Accommodation: {cost_breakdown.get('accommodation_lkr', 0)} LKR")
    lines.append(f"- Food: {cost_breakdown.get('food_lkr', 0)} LKR")
    lines.append(f"- Total: {cost_breakdown.get('total_lkr', 0)} LKR")
    lines.append(f"- Budget: {cost_breakdown.get('budget_lkr', 0)} LKR")
    lines.append("")

    lines.append("## Cultural Notes")
    lines.append("- Dress respectfully at temples and sacred spaces.")
    lines.append("- Remove footwear and hats before entering religious shrines.")
    lines.append("- Support local guides and family-run businesses where possible.")
    lines.append("")

    lines.append("## Safety Tips")
    lines.append("- Start hikes early and carry water, sunscreen, and a charged phone.")
    lines.append("- Confirm weather and transport schedules before long transfers.")
    lines.append("- Keep cash for small shops and remote destinations.")
    lines.append("")

    lines.append("## Personalized Suggestions")
    if personalized_notes:
        for note in personalized_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- Keep one flexible half-day to adjust based on weather and energy levels.")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log_event("tool-report", "report_generation_completed", {"output": str(output_path)})
    return str(output_path)
