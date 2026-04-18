from __future__ import annotations

import argparse
import json

from agents.optimizer_agent import OptimizerAgent
from agents.personalizer_agent import PersonalizerAgent
from agents.research_agent import ResearchAgent
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

    log_event("orchestrator", "workflow_started", {"query": args.query, "model": args.model})
    initialize_tourism_db()
    log_event("orchestrator", "database_ready", {})

    research_agent = ResearchAgent(model=args.model)
    research_result = research_agent.run(user_query=args.query, limit=args.limit)
    log_event(
        "orchestrator",
        "handoff_research_to_optimizer",
        {"records_count": len(research_result.records), "research_model": research_result.model_used},
    )

    optimizer_agent = OptimizerAgent(model=args.model)
    optimizer_result = optimizer_agent.run(user_query=args.query, research_result=research_result)
    log_event(
        "orchestrator",
        "handoff_optimizer_to_personalizer",
        {
            "within_budget": optimizer_result.optimized_plan.get("feasibility", {}).get("within_budget"),
            "optimizer_model": optimizer_result.model_used,
        },
    )

    personalizer_agent = PersonalizerAgent(model=args.model)
    personalizer_result = personalizer_agent.run(
        user_query=args.query,
        optimizer_result=optimizer_result,
        output_filename=args.output,
    )

    output = {
        "query": args.query,
        "research": research_result.__dict__,
        "optimizer": optimizer_result.__dict__,
        "personalizer": personalizer_result.__dict__,
    }
    log_event(
        "orchestrator",
        "workflow_completed",
        {
            "report_path": personalizer_result.report_path,
            "run_log": "logs/run.log",
        },
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()