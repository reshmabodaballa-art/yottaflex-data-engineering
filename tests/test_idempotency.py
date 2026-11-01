
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOADER_SCRIPT = PROJECT_ROOT / "src" / "load_database.py"


def get_database_snapshot(database_path):
    connection = sqlite3.connect(database_path)

    try:
        tables = {
            "customers": "customer_id",
            "products": "product_id",
            "orders": "order_id",
        }

        snapshot = {}

        for table, primary_key in tables.items():
            snapshot[table] = connection.execute(
                f"SELECT * FROM {table} ORDER BY {primary_key}"
            ).fetchall()

        return snapshot

    finally:
        connection.close()


def test_database_loading_is_idempotent(tmp_path):
    # Create an isolated data folder for this test.
    data_folder = tmp_path / "data"
    data_folder.mkdir()

    for filename in (
        "customers.csv",
        "products.csv",
        "orders.csv",
    ):
        source_file = PROJECT_ROOT / "data" / filename
        shutil.copy2(source_file, data_folder / filename)

    database_path = tmp_path / "yottaflex.db"

    # First load creates the database from scratch.
    subprocess.run(
        [sys.executable, str(LOADER_SCRIPT)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    before_snapshot = get_database_snapshot(database_path)

    # Second load must not create duplicate or changed records.
    subprocess.run(
        [sys.executable, str(LOADER_SCRIPT)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    after_snapshot = get_database_snapshot(database_path)

    assert before_snapshot == after_snapshot
