from __future__ import annotations

import argparse
import json

from agents.optimizer_agent import OptimizerAgent
from agents.research_agent import ResearchAgent
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
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    initialize_tourism_db()
    research_agent = ResearchAgent(model=args.model)
    research_result = research_agent.run(user_query=args.query, limit=args.limit)

    optimizer_agent = OptimizerAgent(model=args.model)
    optimizer_result = optimizer_agent.run(user_query=args.query, research_result=research_result)

    output = {
        "query": args.query,
        "research": research_result.__dict__,
        "optimizer": optimizer_result.__dict__,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()