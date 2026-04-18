from tools.tourism_db import initialize_tourism_db, tourism_db_query


def test_tourism_db_query_natural_language_returns_rows():
    initialize_tourism_db()
    rows = tourism_db_query("attractions in ella under 5000 lkr", limit=5)

    assert rows
    assert all("name" in row for row in rows)
    assert all(row["estimated_cost_lkr"] <= 5000 for row in rows)


def test_tourism_db_query_select_sql():
    initialize_tourism_db()
    rows = tourism_db_query("SELECT name, location FROM attractions WHERE location = 'Ella'", limit=3)

    assert len(rows) <= 3
    assert all("name" in row and "location" in row for row in rows)
