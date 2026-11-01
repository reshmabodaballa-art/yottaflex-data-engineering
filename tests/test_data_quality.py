import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from validate_data import validate_data


def test_negative_and_zero_prices():
    df = pd.read_csv("data/test_data/bad_products.csv")
    invalid_prices = df[df["price"] <= 0]
    assert len(invalid_prices) == 2


def test_duplicate_product_ids():
    df = pd.read_csv("data/test_data/bad_products.csv")
    duplicates = df[df.duplicated(
        subset=["product_id"], keep=False
    )]
    assert len(duplicates) == 2


def test_empty_dataset():
    df = pd.DataFrame(columns=[
        "product_id", "product_name", "category", "price"
    ])
    assert df.empty


def test_missing_product_name():
    df = pd.DataFrame({
        "product_id": [1],
        "product_name": [None],
        "category": ["Electronics"],
        "price": [15000]
    })
    assert df["product_name"].isnull().sum() == 1


def test_invalid_order_quantity():
    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "quantity": [2, 0, -1]
    })
    invalid_quantities = df[df["quantity"] <= 0]
    assert len(invalid_quantities) == 2


def test_invalid_order_dates():
    df = pd.DataFrame({
        "order_date": [
            "2026-01-10",
            "invalid-date",
            "2026-02-30"
        ]
    })
    dates = pd.to_datetime(df["order_date"], errors="coerce")
    assert dates.isnull().sum() == 2


def test_validation_saves_invalid_products_to_quarantine(
    tmp_path, monkeypatch
):
    data_folder = tmp_path / "data"
    data_folder.mkdir()

    pd.DataFrame({
        "customer_id": [1],
        "customer_name": ["Test Customer"],
        "city": ["Hyderabad"]
    }).to_csv(data_folder / "customers.csv", index=False)

    pd.DataFrame({
        "product_id": [1],
        "product_name": ["Test Product"],
        "category": ["Electronics"],
        "price": [-100]
    }).to_csv(data_folder / "products.csv", index=False)

    pd.DataFrame({
        "order_id": [1],
        "customer_id": [1],
        "product_id": [1],
        "quantity": [2],
        "order_date": ["2026-01-10"]
    }).to_csv(data_folder / "orders.csv", index=False)

    monkeypatch.chdir(tmp_path)

    result = validate_data()

    rejected_file = data_folder / "quarantine" / "rejected_products.csv"

    assert result is False
    assert rejected_file.exists()

    rejected = pd.read_csv(rejected_file)
    assert "Invalid product price" in rejected["reject_reason"].iloc[0]