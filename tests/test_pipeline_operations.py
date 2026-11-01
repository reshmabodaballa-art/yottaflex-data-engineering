import csv
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate_data import validate_data
from load_database import load_data
import run_pipeline


def write_valid_inputs(folder):
    data = folder / "data"
    data.mkdir(exist_ok=True)
    pd.DataFrame({
        "customer_id": [1],
        "customer_name": ["Customer 1"],
        "city": ["Hyderabad"],
    }).to_csv(data / "customers.csv", index=False)
    pd.DataFrame({
        "product_id": [1],
        "product_name": ["Product 1"],
        "category": ["Books"],
        "price": [100.0],
    }).to_csv(data / "products.csv", index=False)
    pd.DataFrame({
        "order_id": [1, 2],
        "customer_id": [1, 1],
        "product_id": [1, 1],
        "quantity": [2, 1],
        "order_date": ["2026-02-01", "2026-01-01"],
    }).to_csv(data / "orders.csv", index=False)
    return data


def test_validator_rejects_unexpected_schema_change(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    customers = pd.read_csv(data / "customers.csv")
    customers["unexpected_field"] = "new"
    customers.to_csv(data / "customers.csv", index=False)
    monkeypatch.chdir(tmp_path)

    assert validate_data() is False


def test_validator_rejects_malformed_csv(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    (data / "customers.csv").write_text(
        'customer_id,customer_name,city\n1,"broken,Hyderabad\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert validate_data() is False


def test_validator_rejects_empty_batch(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    pd.DataFrame(columns=["customer_id", "customer_name", "city"]).to_csv(
        data / "customers.csv", index=False
    )
    monkeypatch.chdir(tmp_path)

    assert validate_data() is False


def test_validator_rejects_missing_required_value(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    customers = pd.read_csv(data / "customers.csv")
    customers.loc[0, "customer_name"] = None
    customers.to_csv(data / "customers.csv", index=False)
    monkeypatch.chdir(tmp_path)

    assert validate_data() is False
    rejected = pd.read_csv(data / "quarantine" / "rejected_customers.csv")
    assert "Missing required value" in rejected["reject_reason"].iloc[0]


def test_validator_rejects_invalid_foreign_key(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    orders = pd.read_csv(data / "orders.csv")
    orders.loc[0, "customer_id"] = 999
    orders.to_csv(data / "orders.csv", index=False)
    monkeypatch.chdir(tmp_path)

    assert validate_data() is False
    rejected = pd.read_csv(data / "quarantine" / "rejected_orders.csv")
    assert rejected["reject_reason"].str.contains(
        "Invalid customer reference"
    ).any()


def test_out_of_order_event_dates_are_accepted(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)

    # The two valid orders are intentionally not sorted by event date.
    assert validate_data() is True


def test_database_load_rolls_back_partial_batch_and_can_retry(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    orders = pd.read_csv(data / "orders.csv")
    orders.loc[1, "customer_id"] = 999
    orders.to_csv(data / "orders.csv", index=False)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(sqlite3.IntegrityError):
        load_data()

    connection = sqlite3.connect("yottaflex.db")
    try:
        # All inserts in the failed load transaction must roll back.
        assert connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
    finally:
        connection.close()

    # Correct the source and retry the same load.
    orders.loc[1, "customer_id"] = 1
    orders.to_csv(data / "orders.csv", index=False)
    load_data()

    connection = sqlite3.connect("yottaflex.db")
    try:
        assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 2
    finally:
        connection.close()


def test_transient_database_error_is_retried(monkeypatch):
    attempts = {"count": 0}

    def flaky_load():
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise sqlite3.OperationalError("temporary database is locked")

    monkeypatch.setattr(run_pipeline, "load_data", flaky_load)
    run_pipeline._load_with_retry(max_attempts=2, retry_delay=0)

    assert attempts["count"] == 2


def test_pipeline_writes_run_id_and_operational_metrics(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_pipeline, "validate_data", lambda: True)
    monkeypatch.setattr(run_pipeline, "_load_with_retry", lambda: None)
    monkeypatch.setattr(run_pipeline, "sales_analysis", lambda: None)
    monkeypatch.setattr(run_pipeline, "reconcile_data", lambda: True)

    assert run_pipeline.run_pipeline() is True

    history = pd.read_csv(tmp_path / "reports" / "pipeline_runs.csv")
    assert len(history) == 1
    assert history.loc[0, "run_id"]
    assert history.loc[0, "start_time"]
    assert history.loc[0, "end_time"]
    assert history.loc[0, "status"] == "SUCCESS"
    assert "rejected_count" in history.columns
    assert "failure_reason" in history.columns


def test_validator_quarantines_duplicate_primary_keys(tmp_path, monkeypatch):
    data = write_valid_inputs(tmp_path)
    customers = pd.read_csv(data / "customers.csv")
    customers = pd.concat([customers, customers], ignore_index=True)
    customers.to_csv(data / "customers.csv", index=False)
    monkeypatch.chdir(tmp_path)

    assert validate_data() is False
    rejected = pd.read_csv(data / "quarantine" / "rejected_customers.csv")
    assert len(rejected) == 2
    assert rejected["reject_reason"].str.contains("Duplicate ID").all()
