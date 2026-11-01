
import csv
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.generate_data import generate_data


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def test_generator_creates_all_three_files(tmp_path):
    output = tmp_path / "generated"

    generate_data(output, 10, 20, 100, 42)

    assert (output / "customers.csv").exists()
    assert (output / "products.csv").exists()
    assert (output / "orders.csv").exists()


def test_generator_creates_correct_row_counts(tmp_path):
    output = tmp_path / "generated"

    generate_data(output, 10, 20, 100, 42)

    assert len(read_csv(output / "customers.csv")) == 10
    assert len(read_csv(output / "products.csv")) == 20
    assert len(read_csv(output / "orders.csv")) == 100


def test_generator_is_reproducible(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"

    generate_data(first, 10, 20, 100, 42)
    generate_data(second, 10, 20, 100, 42)

    for filename in ["customers.csv", "products.csv", "orders.csv"]:
        assert (first / filename).read_bytes() == (
            second / filename
        ).read_bytes()


def test_generated_orders_have_valid_references(tmp_path):
    output = tmp_path / "generated"

    generate_data(output, 10, 20, 100, 42)

    customers = read_csv(output / "customers.csv")
    products = read_csv(output / "products.csv")
    orders = read_csv(output / "orders.csv")

    customer_ids = {row["customer_id"] for row in customers}
    product_ids = {row["product_id"] for row in products}

    for order in orders:
        assert order["customer_id"] in customer_ids
        assert order["product_id"] in product_ids
        assert int(order["quantity"]) >= 1


def test_generator_rejects_invalid_counts(tmp_path):
    with pytest.raises(ValueError):
        generate_data(tmp_path / "invalid", 0, 20, 100, 42)

    with pytest.raises(ValueError):
        generate_data(tmp_path / "invalid", 10, 0, 100, 42)

    with pytest.raises(ValueError):
        generate_data(tmp_path / "invalid", 10, 20, -1, 42)
