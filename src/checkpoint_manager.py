
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DATABASE = Path("yottaflex.db")

PIPELINE_STAGES = [
    "validation",
    "database_loading",
    "sales_analysis",
    "reconciliation",
]


def get_input_fingerprint(data_folder="data"):
    """Create a SHA-256 fingerprint of all source CSV files."""
    folder = Path(data_folder)
    hasher = hashlib.sha256()

    for filename in [
        "customers.csv",
        "products.csv",
        "orders.csv",
    ]:
        file_path = folder / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required source file is missing: {file_path}"
            )

        hasher.update(filename.encode("utf-8"))

        with file_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                hasher.update(chunk)

    return hasher.hexdigest()


def initialize_checkpoints():
    """Create the checkpoint table if it does not exist."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_checkpoints (
                input_fingerprint TEXT NOT NULL,
                stage TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                run_id TEXT NOT NULL,
                PRIMARY KEY (input_fingerprint, stage)
            )
        """)


def get_completed_stages(input_fingerprint):
    """Return stages completed for the current input files."""
    initialize_checkpoints()

    with sqlite3.connect(DATABASE) as connection:
        rows = connection.execute("""
            SELECT stage
            FROM pipeline_checkpoints
            WHERE input_fingerprint = ?
        """, (input_fingerprint,)).fetchall()

    return {row[0] for row in rows}


def mark_stage_completed(input_fingerprint, stage, run_id):
    """Save a completed stage for the current input files."""
    if stage not in PIPELINE_STAGES:
        raise ValueError(f"Unknown pipeline stage: {stage}")

    initialize_checkpoints()

    completed_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            INSERT OR REPLACE INTO pipeline_checkpoints (
                input_fingerprint,
                stage,
                completed_at,
                run_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            input_fingerprint,
            stage,
            completed_at,
            run_id,
        ))


def clear_checkpoints(input_fingerprint):
    """Remove checkpoints for one specific input version."""
    initialize_checkpoints()

    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            DELETE FROM pipeline_checkpoints
            WHERE input_fingerprint = ?
        """, (input_fingerprint,))
