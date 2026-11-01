import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import checkpoint_manager as checkpoints


def create_input_files(folder):
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "customers.csv").write_text(
        "customer_id,customer_name,city\n1,Asha,Hyderabad\n",
        encoding="utf-8"
    )
    (folder / "products.csv").write_text(
        "product_id,product_name,category,price\n1,Book,Books,100\n",
        encoding="utf-8"
    )
    (folder / "orders.csv").write_text(
        "order_id,customer_id,product_id,quantity,order_date\n"
        "1,1,1,2,2026-01-01\n",
        encoding="utf-8"
    )


def test_fingerprint_is_reproducible(tmp_path):
    data = tmp_path / "data"
    create_input_files(data)

    first = checkpoints.get_input_fingerprint(data)
    second = checkpoints.get_input_fingerprint(data)

    assert first == second


def test_fingerprint_changes_when_source_changes(tmp_path):
    data = tmp_path / "data"
    create_input_files(data)

    first = checkpoints.get_input_fingerprint(data)

    with (data / "orders.csv").open("a", encoding="utf-8") as file:
        file.write("2,1,1,3,2026-01-02\n")

    second = checkpoints.get_input_fingerprint(data)

    assert first != second


def test_completed_stage_is_saved_and_retrieved(tmp_path, monkeypatch):
    database = tmp_path / "test.db"
    monkeypatch.setattr(checkpoints, "DATABASE", database)

    fingerprint = "test-fingerprint"

    checkpoints.mark_stage_completed(
        fingerprint, "validation", "run-001"
    )

    completed = checkpoints.get_completed_stages(fingerprint)

    assert "validation" in completed


def test_different_input_has_no_old_checkpoints(tmp_path, monkeypatch):
    database = tmp_path / "test.db"
    monkeypatch.setattr(checkpoints, "DATABASE", database)

    checkpoints.mark_stage_completed(
        "fingerprint-one", "validation", "run-001"
    )

    completed = checkpoints.get_completed_stages(
        "fingerprint-two"
    )

    assert completed == set()


def test_unknown_stage_is_rejected(tmp_path, monkeypatch):
    database = tmp_path / "test.db"
    monkeypatch.setattr(checkpoints, "DATABASE", database)

    with pytest.raises(ValueError):
        checkpoints.mark_stage_completed(
            "test-fingerprint", "unknown-stage", "run-001"
        )


def test_checkpoints_can_be_cleared(tmp_path, monkeypatch):
    database = tmp_path / "test.db"
    monkeypatch.setattr(checkpoints, "DATABASE", database)

    fingerprint = "test-fingerprint"

    checkpoints.mark_stage_completed(
        fingerprint, "validation", "run-001"
    )

    checkpoints.clear_checkpoints(fingerprint)

    assert checkpoints.get_completed_stages(fingerprint) == set()


def test_missing_input_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        checkpoints.get_input_fingerprint(tmp_path / "missing")
