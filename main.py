from __future__ import annotations

import argparse
import json

from agents.research_agent import ResearchAgent
from tools.tourism_db import initialize_tourism_db


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LankaVoyage AI - Research Agent Runner"
    )
    parser.add_argument("query", help="User research request")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of verified records to fetch",
    )
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Ollama model name for summarization",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    initialize_tourism_db()
    agent = ResearchAgent(model=args.model)
    result = agent.run(user_query=args.query, limit=args.limit)

    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()