from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib import error, request

from agents.optimizer_agent import OptimizerAgentResult
from tools.observability import log_event
from tools.report_generator import report_generator


@dataclass
class PersonalizerAgentResult:
    query: str
    personalized_plan: Dict[str, Any]
    personalized_summary: str
    report_path: str
    model_used: str
    used_fallback: bool


class PersonalizerAgent:
    """Personalizer agent that formats and enriches the optimized itinerary."""

    def __init__(
        self,
        model: str = "llama3.2",
        ollama_url: str = "http://localhost:11434/api/generate",
        request_timeout_seconds: int = 90,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.request_timeout_seconds = request_timeout_seconds

    def run(self, user_query: str, optimizer_result: OptimizerAgentResult) -> PersonalizerAgentResult:
        log_event(
            "personalizer",
            "agent_started",
            {
                "query": user_query,
                "optimizer_model": optimizer_result.model_used,
                "optimizer_used_fallback": optimizer_result.used_fallback,
            },
        )

        personalized_plan = dict(optimizer_result.optimized_plan)
        notes = self._build_personalized_notes(user_query, personalized_plan)
        personalized_plan["personalized_notes"] = notes
        log_event("personalizer", "notes_created", {"notes_count": len(notes)})

        prompt = self._build_prompt(user_query, optimizer_result.summary, personalized_plan)
        log_event("personalizer", "llm_request_prepared", {"model": self.model, "prompt_chars": len(prompt)})
        llm_response = self._call_ollama(prompt)

        if llm_response is None:
            personalized_summary = self._fallback_summary(personalized_plan)
            used_fallback = True
            model_used = "fallback"
            log_event("personalizer", "fallback_used", {"reason": "llm_unavailable_or_invalid"})
        else:
            personalized_summary = llm_response
            used_fallback = False
            model_used = self.model

        personalized_plan["personalized_summary"] = personalized_summary
        report_path = report_generator(personalized_plan)

        result = PersonalizerAgentResult(
            query=user_query,
            personalized_plan=personalized_plan,
            personalized_summary=personalized_summary,
            report_path=report_path,
            model_used=model_used,
            used_fallback=used_fallback,
        )
        log_event(
            "personalizer",
            "agent_completed",
            {"model_used": model_used, "used_fallback": used_fallback, "report_path": report_path},
        )
        return result

    def _build_personalized_notes(self, user_query: str, plan: Dict[str, Any]) -> List[str]:
        lowered = user_query.lower()
        notes: List[str] = []

        if "couple" in lowered:
            notes.append("Reserve a scenic dinner slot in Ella town on the second evening.")
        if "hiking" in lowered or "nature" in lowered:
            notes.append("Start outdoor activities before 8:00 AM to avoid midday heat and crowds.")
        if "budget" in lowered or "under" in lowered:
            notes.append("Keep a small contingency buffer for transport delays and rain-plan changes.")

        selected = plan.get("selected_attractions", [])
        if selected:
            notes.append(f"Prioritize {selected[0].get('name', 'the first attraction')} on Day 1 for an easy start.")

        if not notes:
            notes.append("Keep one flexible block for weather-dependent adjustments.")

        return notes

    def _build_prompt(self, user_query: str, optimizer_summary: str, personalized_plan: Dict[str, Any]) -> str:
        return (
            "You are LankaVoyage AI Personalizer Agent.\n"
            "Refine this itinerary summary for user readability and confidence.\n"
            "Keep it realistic and grounded in the provided plan only.\n"
            "Include a concise final recommendation.\n"
            f"User request: {user_query}\n"
            f"Optimizer summary:\n{optimizer_summary}\n"
            f"Personalized plan:\n{json.dumps(personalized_plan, indent=2, ensure_ascii=False)}"
        )

    def _call_ollama(self, prompt: str) -> str | None:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        }
        req = request.Request(
            self.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        for attempt in range(1, 3):
            try:
                log_event("personalizer", "llm_call_attempt", {"attempt": attempt, "model": self.model})
                with request.urlopen(req, timeout=self.request_timeout_seconds) as response:
                    parsed = json.loads(response.read().decode("utf-8"))
                    text = parsed.get("response", "").strip()
                    return text if text else None
            except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                log_event("personalizer", "llm_call_failed", {"attempt": attempt})
                if attempt == 1:
                    continue
                return None

    def _fallback_summary(self, personalized_plan: Dict[str, Any]) -> str:
        cost = personalized_plan.get("cost_breakdown", {}).get("total_lkr", 0)
        days = personalized_plan.get("trip_summary", {}).get("days", "?")
        return (
            "Personalizer summary: your itinerary is organized into a readable day-by-day flow with "
            f"clear budget visibility. Planned duration is {days} day(s), with an estimated total of {cost} LKR."
        )
