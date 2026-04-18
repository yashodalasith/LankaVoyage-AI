from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = WORKSPACE_ROOT / "data" / "sri_lanka_tourism.db"
DEFAULT_SEED_SQL_PATH = WORKSPACE_ROOT / "data" / "tourism_seed.sql"


def initialize_tourism_db(
    db_path: Path = DEFAULT_DB_PATH,
    seed_sql_path: Path = DEFAULT_SEED_SQL_PATH,
) -> None:
    """Initializes and seeds the local tourism database if missing."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        return

    if not seed_sql_path.exists():
        raise FileNotFoundError(f"Seed SQL not found: {seed_sql_path}")

    sql_script = seed_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as connection:
        connection.executescript(sql_script)
        connection.commit()


def tourism_db_query(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Queries the local Sri Lankan tourism SQLite database for verified travel data.

    Args:
        query: Natural language or SQL query.
        limit: Maximum number of rows in the result.

    Returns:
        List of dictionaries containing matching records.
    """
    try:
        initialize_tourism_db()
        normalized_limit = max(1, min(int(limit), 50))
        query_text = query.strip()

        if not query_text:
            return [{"error": "Query cannot be empty."}]

        with sqlite3.connect(DEFAULT_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            if query_text.lower().startswith("select"):
                safe_sql = f"SELECT * FROM ({query_text.rstrip(';')}) LIMIT ?"
                cursor.execute(safe_sql, (normalized_limit,))
                return [dict(row) for row in cursor.fetchall()]

            return _search_from_text(cursor, query_text, normalized_limit)
    except Exception as exc:  # pragma: no cover - defensive path
        return [{"error": f"Database query failed: {exc}"}]


def _search_from_text(
    cursor: sqlite3.Cursor,
    query_text: str,
    limit: int,
) -> List[Dict[str, Any]]:
    lowered = query_text.lower()

    budget_cap = _extract_budget_cap(lowered)
    location = _extract_location(cursor, lowered)
    category = _extract_category(lowered)

    sql = (
        "SELECT name, location, district, category, estimated_cost_lkr, avg_duration_hours, description "
        "FROM attractions WHERE 1=1"
    )
    params: List[Any] = []

    if location:
        sql += " AND (LOWER(location) LIKE ? OR LOWER(district) LIKE ?)"
        wildcard = f"%{location.lower()}%"
        params.extend([wildcard, wildcard])

    if category:
        sql += " AND LOWER(category) = ?"
        params.append(category)

    if budget_cap is not None:
        sql += " AND estimated_cost_lkr <= ?"
        params.append(budget_cap)

    sql += " ORDER BY estimated_cost_lkr ASC, avg_duration_hours ASC LIMIT ?"
    params.append(limit)

    cursor.execute(sql, params)
    rows = [dict(row) for row in cursor.fetchall()]

    if rows:
        return rows

    # Fallback broad match across attraction names and descriptions.
    cursor.execute(
        """
        SELECT name, location, district, category, estimated_cost_lkr, avg_duration_hours, description
        FROM attractions
        WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?
        ORDER BY estimated_cost_lkr ASC
        LIMIT ?
        """,
        (f"%{lowered}%", f"%{lowered}%", limit),
    )
    return [dict(row) for row in cursor.fetchall()]


def _extract_budget_cap(lowered_query: str) -> int | None:
    tokens = lowered_query.replace(",", " ").split()
    keywords = {"under", "below", "max", "budget"}

    for idx, token in enumerate(tokens):
        if token in keywords and idx + 1 < len(tokens):
            next_token = tokens[idx + 1].replace("lkr", "").strip()
            if next_token.isdigit():
                return int(next_token)

    for token in tokens:
        stripped = token.replace("lkr", "")
        if stripped.isdigit() and len(stripped) >= 3:
            return int(stripped)

    return None


def _extract_location(cursor: sqlite3.Cursor, lowered_query: str) -> str | None:
    cursor.execute("SELECT DISTINCT location FROM attractions")
    locations = [row[0].lower() for row in cursor.fetchall()]

    for location in locations:
        if location in lowered_query:
            return location

    return None


def _extract_category(lowered_query: str) -> str | None:
    category_aliases = {
        "hike": "hiking",
        "hiking": "hiking",
        "beach": "beach",
        "wildlife": "wildlife",
        "safari": "wildlife",
        "heritage": "heritage",
        "culture": "heritage",
        "nature": "nature",
        "adventure": "adventure",
        "marine": "marine",
        "tea": "tea",
    }

    for key, canonical in category_aliases.items():
        if key in lowered_query:
            return canonical

    return None
