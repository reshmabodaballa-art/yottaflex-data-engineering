
import pandas as pd
from pathlib import Path


def validate_data():
    data_folder = Path("data")

    required_columns = {
        "customers": ["customer_id", "customer_name", "city"],
        "products": ["product_id", "product_name", "category", "price"],
        "orders": [
            "order_id", "customer_id", "product_id",
            "quantity", "order_date"
        ]
    }

    print("Starting data validation...\n")

    datasets = {}
    errors = []

    # Check files, empty datasets and required columns
    for name, columns in required_columns.items():
        file_path = data_folder / f"{name}.csv"

        if not file_path.exists():
            errors.append(f"{name}.csv is missing")
            continue

        df = pd.read_csv(file_path)

        if df.empty:
            errors.append(f"{name}.csv is empty")

        missing_columns = set(columns) - set(df.columns)

        if missing_columns:
            errors.append(
                f"Missing columns in {name}: {missing_columns}"
            )
            continue

        datasets[name] = df

    if len(datasets) != 3:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return False

    customers = datasets["customers"]
    products = datasets["products"]
    orders = datasets["orders"]

    # Check missing values
    for name, df in datasets.items():
        missing = df.isnull().sum().sum()
        print(f"{name} missing values: {missing}")

        if missing > 0:
            errors.append(f"{name} contains missing values")

    # Check duplicate IDs
    duplicate_checks = {
        "Customer IDs": customers["customer_id"],
        "Product IDs": products["product_id"],
        "Order IDs": orders["order_id"]
    }

    for label, column in duplicate_checks.items():
        duplicates = column.duplicated().sum()
        print(f"{label} duplicates: {duplicates}")

        if duplicates > 0:
            errors.append(f"{label} contain duplicates")

    # Check product prices
    invalid_prices = products["price"] <= 0
    print("Invalid product prices:", invalid_prices.sum())

    if invalid_prices.any():
        errors.append("Invalid product prices found")

    # Check order quantities
    invalid_quantities = orders["quantity"] <= 0
    print("Invalid order quantities:", invalid_quantities.sum())

    if invalid_quantities.any():
        errors.append("Invalid order quantities found")

    # Check order dates
    invalid_dates = pd.to_datetime(
        orders["order_date"], errors="coerce"
    ).isna()

    print("Invalid order dates:", invalid_dates.sum())

    if invalid_dates.any():
        errors.append("Invalid order dates found")

    # Check customer and product references
    invalid_customers = ~orders["customer_id"].isin(
        customers["customer_id"]
    )
    invalid_products = ~orders["product_id"].isin(
        products["product_id"]
    )

    print("Invalid customer references:", invalid_customers.sum())
    print("Invalid product references:", invalid_products.sum())

    if invalid_customers.any():
        errors.append("Invalid customer references found")

    if invalid_products.any():
        errors.append("Invalid product references found")

    # Final validation result
    print("\nValidation Summary:")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return False

    print("VALIDATION PASSED")
    print("All data quality checks passed successfully.")
    return True


if __name__ == "__main__":
    validate_data()
