import pandas as pd


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


