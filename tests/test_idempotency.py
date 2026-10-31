
import sqlite3
import subprocess
import sys


def test_database_loading_is_idempotent():
    connection = sqlite3.connect("yottaflex.db")

    tables = ["customers", "products", "orders"]

    before_counts = {}

    for table in tables:
        before_counts[table] = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

    connection.close()

    subprocess.run(
        [sys.executable, "src/load_database.py"],
        check=True,
        capture_output=True,
        text=True
    )

    connection = sqlite3.connect("yottaflex.db")

    after_counts = {}

    for table in tables:
        after_counts[table] = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

    connection.close()

    assert before_counts == after_counts
