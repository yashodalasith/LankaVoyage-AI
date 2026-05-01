from __future__ import annotations

import argparse
import json

from tools.graph_orchestrator import run_planning_workflow
from tools.observability import log_event
from tools.tourism_db import initialize_tourism_db


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LankaVoyage AI - Orchestrated Research and Optimizer Runner"
    )
    parser.add_argument("query", help="User travel planning request")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of verified records to fetch for the research stage",
    )
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Ollama model name used by both agents",
    )
    parser.add_argument(
        "--output",
        default="itinerary.md",
        help="Output markdown filename for the personalized itinerary",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    # Initialize database
    log_event("orchestrator", "workflow_started", {"query": args.query, "model": args.model})
    initialize_tourism_db()
    log_event("orchestrator", "database_ready", {})

    # Run the LangGraph workflow
    final_state = run_planning_workflow(
        query=args.query,
        model=args.model,
        limit=args.limit,
        output_filename=args.output,
    )

    # Build output JSON with full workflow results
    output = {
        "query": final_state.query,
        "research": {
            "records": final_state.research_records,
            "summary": final_state.research_summary,
            "model_used": final_state.research_model_used,
            "used_fallback": final_state.research_used_fallback,
        },
        "optimizer": {
            "preferences": final_state.preferences,
            "optimized_plan": final_state.optimized_plan,
            "summary": final_state.optimizer_summary,
            "model_used": final_state.optimizer_model_used,
            "used_fallback": final_state.optimizer_used_fallback,
        },
        "personalizer": {
            "personalized_plan": final_state.personalized_plan,
            "personalized_summary": final_state.personalized_summary,
            "report_path": final_state.report_path,
            "model_used": final_state.personalizer_model_used,
            "used_fallback": final_state.personalizer_used_fallback,
        },
    }

    log_event(
        "orchestrator",
        "workflow_completed",
        {
            "report_path": final_state.report_path,
            "run_log": "logs/run.log",
        },
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()