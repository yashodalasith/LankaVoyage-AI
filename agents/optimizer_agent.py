from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib import error, request

from agents.research_agent import ResearchAgentResult
from tools.itinerary_optimizer import itinerary_optimizer
from tools.observability import log_event
from tools.trace_logger import append_trace


@dataclass
class OptimizerAgentResult:
    query: str
    preferences: Dict[str, Any]
    optimized_plan: Dict[str, Any]
    summary: str
    model_used: str
    used_fallback: bool


class OptimizerAgent:
    """Optimizer agent that turns verified research data into a feasible itinerary."""

    def __init__(
        self,
        model: str = "llama3.2",
        ollama_url: str = "http://localhost:11434/api/generate",
        request_timeout_seconds: int = 90,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.request_timeout_seconds = request_timeout_seconds

    def run(self, user_query: str, research_result: ResearchAgentResult) -> OptimizerAgentResult:
        log_event(
            "optimizer",
            "agent_started",
            {
                "query": user_query,
                "research_model": research_result.model_used,
                "research_used_fallback": research_result.used_fallback,
            },
        )
        preferences = self._parse_preferences(user_query)
        log_event("optimizer", "preferences_parsed", preferences)
        append_trace(
            "optimizer_agent_input",
            {
                "query": user_query,
                "preferences": preferences,
                "research_model": research_result.model_used,
                "research_used_fallback": research_result.used_fallback,
            },
        )

        optimized_plan = itinerary_optimizer(
            research_data=research_result.records,
            budget=preferences["budget_lkr"],
            days=preferences["days"],
            preferences=preferences,
        )
        log_event(
            "optimizer",
            "planning_engine_completed",
            {
                "selected_attractions": len(optimized_plan.get("selected_attractions", [])),
                "within_budget": optimized_plan.get("feasibility", {}).get("within_budget"),
            },
        )

        prompt = self._build_prompt(user_query, research_result.summary, optimized_plan)
        log_event("optimizer", "llm_request_prepared", {"model": self.model, "prompt_chars": len(prompt)})
        llm_response = self._call_ollama(prompt)
        if llm_response is None:
            summary = self._fallback_summary(optimized_plan)
            model_used = "fallback"
            used_fallback = True
            log_event("optimizer", "fallback_used", {"reason": "llm_unavailable_or_invalid"})
        else:
            summary = llm_response
            model_used = self.model
            used_fallback = False

        result = OptimizerAgentResult(
            query=user_query,
            preferences=preferences,
            optimized_plan=optimized_plan,
            summary=summary,
            model_used=model_used,
            used_fallback=used_fallback,
        )
        append_trace("optimizer_agent_output", result.__dict__)
        log_event("optimizer", "agent_completed", {"model_used": model_used, "used_fallback": used_fallback})
        return result

    def _parse_preferences(self, user_query: str) -> Dict[str, Any]:
        lowered = user_query.lower()
        budget_match = re.search(r"(?:under|max(?:imum)?|budget(?:\s+of)?)\s+([0-9][0-9,]*)\s*lkr", lowered)
        days_match = re.search(r"([0-9]+)\s*[- ]?day", lowered)
        route_match = re.search(r"to\s+([a-z ]+?)\s+from\s+([a-z ]+?)(?:\s+under|\s+max|\s+budget|$)", lowered)

        destination = "Unknown"
        origin = "Unknown"
        if route_match:
            destination = route_match.group(1).strip().title()
            origin = route_match.group(2).strip().title()

        interests = [
            keyword
            for keyword in ["hiking", "nature", "beach", "wildlife", "culture", "heritage", "adventure", "tea"]
            if keyword in lowered
        ]

        return {
            "budget_lkr": int(budget_match.group(1).replace(",", "")) if budget_match else 80000,
            "days": int(days_match.group(1)) if days_match else 4,
            "origin": origin,
            "destination": destination,
            "interests": interests,
        }

    def _build_prompt(self, user_query: str, research_summary: str, optimized_plan: Dict[str, Any]) -> str:
        return (
            "You are LankaVoyage AI Optimizer Agent.\n"
            "Use the verified research summary and the structured optimization plan below.\n"
            "Do not invent attractions, prices, or transport facts.\n"
            "Return a concise explanation that confirms the itinerary is feasible or explains the shortfall.\n"
            f"User request: {user_query}\n"
            f"Research summary:\n{research_summary}\n"
            f"Optimization trace:\n{json.dumps(optimized_plan, indent=2, ensure_ascii=False)}"
        )

    def _call_ollama(self, prompt: str) -> str | None:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        req = request.Request(
            self.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        for attempt in range(1, 3):
            try:
                log_event("optimizer", "llm_call_attempt", {"attempt": attempt, "model": self.model})
                with request.urlopen(req, timeout=self.request_timeout_seconds) as response:
                    parsed = json.loads(response.read().decode("utf-8"))
                    text = parsed.get("response", "").strip()
                    return text if text else None
            except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                log_event("optimizer", "llm_call_failed", {"attempt": attempt})
                if attempt == 1:
                    continue
                return None

    def _fallback_summary(self, optimized_plan: Dict[str, Any]) -> str:
        cost_breakdown = optimized_plan.get("cost_breakdown", {})
        feasibility = optimized_plan.get("feasibility", {})
        return (
            "Optimizer summary: the itinerary was assembled from verified local data and budget-checked before finalization. "
            f"Total estimated cost is {cost_breakdown.get('total_lkr', 0)} LKR against the trip budget of {cost_breakdown.get('budget_lkr', 0)} LKR. "
            f"Feasibility checks show within_budget={feasibility.get('within_budget')} and within_days={feasibility.get('within_days')}."
        )
