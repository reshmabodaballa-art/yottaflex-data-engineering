
import csv
import logging
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from validate_data import validate_data
from load_database import load_data
from sales_analysis import sales_analysis
from reconciliation import reconcile_data
from checkpoint_manager import (
    get_input_fingerprint,
    mark_stage_completed,
)

REPORT_DIR = Path("reports")
RUN_HISTORY = REPORT_DIR / "pipeline_runs.csv"
REPORT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=REPORT_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)

RUN_FIELDS = [
    "run_id", "start_time", "end_time", "status",
    "customers_input", "products_input", "orders_input",
    "customers_output", "products_output", "orders_output",
    "rejected_count", "duration_seconds", "failure_reason",
]


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _csv_row_count(path):
    try:
        import pandas as pd

        if not Path(path).exists():
            return 0

        return len(pd.read_csv(path))

    except Exception:
        return 0


def _input_counts():
    return {
        "customers_input": _csv_row_count("data/customers.csv"),
        "products_input": _csv_row_count("data/products.csv"),
        "orders_input": _csv_row_count("data/orders.csv"),
    }


def _output_counts():
    counts = {
        "customers_output": 0,
        "products_output": 0,
        "orders_output": 0,
    }

    if not Path("yottaflex.db").exists():
        return counts

    try:
        with sqlite3.connect("yottaflex.db") as connection:
            for table in ("customers", "products", "orders"):
                counts[f"{table}_output"] = connection.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

    except sqlite3.Error:
        pass

    return counts


def _rejected_count():
    import pandas as pd

    total = 0
    quarantine = Path("data/quarantine")

    if not quarantine.exists():
        return total

    for path in quarantine.glob("rejected_*.csv"):
        try:
            total += len(pd.read_csv(path))
        except Exception:
            continue

    return total


def _append_run_record(record):
    REPORT_DIR.mkdir(exist_ok=True)
    write_header = not RUN_HISTORY.exists()

    with RUN_HISTORY.open(
        "a", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=RUN_FIELDS)

        if write_header:
            writer.writeheader()

        writer.writerow(record)


def _load_with_retry(run_id, max_attempts=3, retry_delay=0.25):
    """Retry database loading attempts."""
    for attempt in range(1, max_attempts + 1):
        try:
            load_data(run_id=run_id)
            return

        except sqlite3.OperationalError:
            if attempt == max_attempts:
                raise

            logging.warning(
                "Database load attempt %s/%s failed; retrying.",
                attempt,
                max_attempts,
            )
            time.sleep(retry_delay * attempt)


def run_pipeline():
    run_id = str(uuid.uuid4())
    start_time = _utc_now()
    started = time.perf_counter()

    status = "FAILED"
    failure_reason = ""

    print("=" * 50)
    print("YOTTAFLEX AI - DATA PIPELINE")
    print(f"Run ID: {run_id}")
    print("=" * 50)

    logging.info("Pipeline run %s started.", run_id)

    try:
        input_fingerprint = get_input_fingerprint("data")
        print("\nInput fingerprint:", input_fingerprint)

        # Checkpoints are recorded for history.
        # They are not used to skip stages because database
        # contents and report files may have changed or disappeared.

        print("\nSTEP 1: DATA VALIDATION")

        if not validate_data():
            raise ValueError(
                "Data validation failed; inspect quarantine and pipeline log."
            )

        mark_stage_completed(
            input_fingerprint, "validation", run_id
        )
        logging.info("Run %s: validation completed.", run_id)

        print("\nSTEP 2: DATABASE LOADING")

        _load_with_retry(run_id)

        mark_stage_completed(
            input_fingerprint, "database_loading", run_id
        )
        logging.info("Run %s: database loading completed.", run_id)

        print("\nSTEP 3: SALES ANALYSIS")

        sales_analysis()

        mark_stage_completed(
            input_fingerprint, "sales_analysis", run_id
        )
        logging.info("Run %s: sales analysis completed.", run_id)
        print("\nSTEP 4: DATA RECONCILIATION")

        if not reconcile_data():
            raise ValueError(
                "Data reconciliation failed; inspect reconciliation_report.pending.csv."
            )

        # Publish reports only after reconciliation succeeds.
        sales_pending = REPORT_DIR / "sales_analysis.pending.csv"
        reconciliation_pending = (
            REPORT_DIR / "reconciliation_report.pending.csv"
        )

        sales_pending.replace(REPORT_DIR / "sales_analysis.csv")
        reconciliation_pending.replace(
            REPORT_DIR / "reconciliation_report.csv"
        )

        mark_stage_completed(
            input_fingerprint, "reconciliation", run_id
        )
        logging.info("Run %s: reconciliation completed.", run_id)
        
        status = "SUCCESS"

        print("\n" + "=" * 50)
        print("DATA PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)

        return True

    except Exception as error:
        failure_reason = f"{type(error).__name__}: {error}"

        logging.exception("Run %s failed.", run_id)

        print("\nPipeline failed.")
        print("Reason:", failure_reason)
        print("Check reports/pipeline.log for details.")

        return False

    finally:
        ended = time.perf_counter()

        record = {
            "run_id": run_id,
            "start_time": start_time,
            "end_time": _utc_now(),
            "status": status,
            **_input_counts(),
            **_output_counts(),
            "rejected_count": _rejected_count(),
            "duration_seconds": round(ended - started, 4),
            "failure_reason": failure_reason,
        }

        _append_run_record(record)

        logging.info(
            "Run %s finished with status %s in %.4f seconds.",
            run_id,
            status,
            ended - started,
        )

        print(f"Run status: {status}")
        print(f"Run ID: {run_id}")
        print(f"Operational metrics: {RUN_HISTORY}")

if __name__ == "__main__":
    import sys
    sys.exit(0 if run_pipeline() else 1)
