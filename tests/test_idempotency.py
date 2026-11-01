import sqlite3
import subprocess
import sys


def get_database_snapshot():
    connection = sqlite3.connect("yottaflex.db")

    try:
        tables = {
            "customers": "customer_id",
            "products": "product_id",
            "orders": "order_id"
        }

        snapshot = {}

        for table, primary_key in tables.items():
            snapshot[table] = connection.execute(
                f"SELECT * FROM {table} ORDER BY {primary_key}"
            ).fetchall()

        return snapshot

    finally:
        connection.close()


def test_database_loading_is_idempotent():
    before_snapshot = get_database_snapshot()

    subprocess.run(
        [sys.executable, "src/load_database.py"],
        check=True,
        capture_output=True,
        text=True
    )

    after_snapshot = get_database_snapshot()

    assert before_snapshot == after_snapshot