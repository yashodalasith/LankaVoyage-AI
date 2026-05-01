from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib import error, request

from tools.graph_state import PlanningState
from tools.observability import log_event
from tools.tourism_db import tourism_db_query


@dataclass
class ResearchAgentResult:
    query: str
    records: List[Dict[str, Any]]
    summary: str
    model_used: str
    used_fallback: bool


class ResearchAgent:
    """Research agent that gathers verified data and summarizes with a local LLM."""

    def __init__(
        self,
        model: str = "llama3.2",
        ollama_url: str = "http://localhost:11434/api/generate",
        request_timeout_seconds: int = 90,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.request_timeout_seconds = request_timeout_seconds

    def run(self, user_query: str, limit: int = 10) -> ResearchAgentResult:
        log_event("research", "agent_started", {"query": user_query, "limit": limit})
        records = tourism_db_query(user_query, limit=limit)
        log_event("research", "tool_response_received", {"records_count": len(records)})
        if records and "error" in records[0]:
            fallback = f"Unable to retrieve tourism facts: {records[0]['error']}"
            log_event("research", "tool_error", {"error": records[0]["error"]})
            return ResearchAgentResult(
                query=user_query,
                records=[],
                summary=fallback,
                model_used="none",
                used_fallback=True,
            )

        prompt = self._build_prompt(user_query, records)
        log_event("research", "llm_request_prepared", {"model": self.model, "prompt_chars": len(prompt)})
        llm_response = self._call_ollama(prompt)

        if llm_response is None:
            summary = self._fallback_summary(user_query, records)
            log_event("research", "fallback_used", {"reason": "llm_unavailable_or_invalid"})
            return ResearchAgentResult(
                query=user_query,
                records=records,
                summary=summary,
                model_used="fallback",
                used_fallback=True,
            )

        log_event("research", "agent_completed", {"model_used": self.model, "used_fallback": False})
        return ResearchAgentResult(
            query=user_query,
            records=records,
            summary=llm_response,
            model_used=self.model,
            used_fallback=False,
        )

    def _build_prompt(self, user_query: str, records: List[Dict[str, Any]]) -> str:
        rows = "\n".join(
            [
                (
                    f"- {row['name']} ({row['location']}, {row['district']}) | "
                    f"category={row['category']} | cost_lkr={row['estimated_cost_lkr']} | "
                    f"duration_hours={row['avg_duration_hours']}"
                )
                for row in records
            ]
        )

        return (
            "You are LankaVoyage AI Research Agent.\n"
            "Use only the verified records below. Do not hallucinate locations, prices, or timings.\n"
            "Return a concise research summary with:\n"
            "1) best matching places\n"
            "2) approximate cost implications\n"
            "3) quick travel suitability notes\n"
            f"User request: {user_query}\n"
            f"Verified records:\n{rows}"
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

        attempts = 2
        for attempt in range(1, attempts + 1):
            try:
                log_event("research", "llm_call_attempt", {"attempt": attempt, "model": self.model})
                with request.urlopen(req, timeout=self.request_timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    parsed = json.loads(body)
                    text = parsed.get("response", "").strip()
                    return text if text else None
            except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                log_event("research", "llm_call_failed", {"attempt": attempt})
                if attempt < attempts:
                    time.sleep(1)
                    continue
                return None

    def _fallback_summary(self, user_query: str, records: List[Dict[str, Any]]) -> str:
        if not records:
            return "No matching verified attractions found for the current query."

        lines = [f"Research findings for: {user_query}"]
        for row in records[:5]:
            lines.append(
                (
                    f"- {row['name']} in {row['location']} ({row['category']}), "
                    f"estimated entry/activity cost around {row['estimated_cost_lkr']} LKR, "
                    f"typically {row['avg_duration_hours']} hours."
                )
            )

        return "\n".join(lines)


# LangGraph node function
def research_node(state: PlanningState) -> PlanningState:
    """LangGraph node that runs the research agent and updates state.
    
    This node is called by the LangGraph StateGraph workflow.
    It takes the current planning state, runs the research agent,
    and returns the updated state with research outputs.
    """
    log_event(
        "graph_node",
        "research_node_started",
        {"query": state.query, "model": state.model},
    )

    agent = ResearchAgent(model=state.model)
    result = agent.run(user_query=state.query, limit=state.limit)

    # Update state with research outputs
    state.research_records = result.records
    state.research_summary = result.summary
    state.research_model_used = result.model_used
    state.research_used_fallback = result.used_fallback

    log_event(
        "graph_node",
        "research_node_completed",
        {
            "records_count": len(result.records),
            "model_used": result.model_used,
            "used_fallback": result.used_fallback,
        },
    )

    return state

