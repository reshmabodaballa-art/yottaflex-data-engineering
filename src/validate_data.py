
import pandas as pd
from pathlib import Path


def validate_data():
    data_folder = Path("data")
    quarantine_folder = data_folder / "quarantine"
    quarantine_folder.mkdir(parents=True, exist_ok=True)
    # Remove only prior validator outputs so rejected_count reflects this run.
    for old_report in quarantine_folder.glob("rejected_*.csv"):
        old_report.unlink()

    required_columns = {
        "customers": ["customer_id", "customer_name", "city"],
        "products": ["product_id", "product_name", "category", "price"],
        "orders": [
            "order_id", "customer_id", "product_id",
            "quantity", "order_date"
        ]
    }

    datasets = {}
    rejected_records = {}
    errors = []

    print("Starting data validation...\n")

    # Step 1: Read files and check schemas
    for name, columns in required_columns.items():
        file_path = data_folder / f"{name}.csv"

        if not file_path.exists():
            errors.append(f"{name}.csv is missing")
            continue

        try:
            df = pd.read_csv(file_path)
        except (pd.errors.ParserError, UnicodeDecodeError, OSError) as error:
            errors.append(f"Could not read {name}.csv: {error}")
            continue

        missing_columns = set(columns) - set(df.columns)
        unexpected_columns = set(df.columns) - set(columns)

        if missing_columns or unexpected_columns:
            if missing_columns:
                errors.append(
                    f"Missing columns in {name}.csv: {sorted(missing_columns)}"
                )
            if unexpected_columns:
                errors.append(
                    f"Unexpected columns in {name}.csv: {sorted(unexpected_columns)}"
                )
            continue

        if df.empty:
            errors.append(f"{name}.csv is empty")
            continue

        df = df.copy()
        df["_source_row"] = range(2, len(df) + 2)
        datasets[name] = df

    # Stop if a required dataset or schema is unavailable
    if len(datasets) != 3:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return False

    customers = datasets["customers"]
    products = datasets["products"]
    orders = datasets["orders"]

    # Step 2: Identify invalid rows
    def add_rejections(name, df, mask, reason):
        if mask.any():
            rejected = df.loc[mask].copy()
            rejected["reject_reason"] = reason
            rejected["source_file"] = f"{name}.csv"

            rejected_records.setdefault(name, []).append(rejected)

    # Missing values
    for name, df in datasets.items():
        missing_mask = df[required_columns[name]].isnull().any(axis=1)
        add_rejections(name, df, missing_mask, "Missing required value")

    # Duplicate IDs
    id_columns = {
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id"
    }

    for name, id_column in id_columns.items():
        df = datasets[name]
        duplicate_mask = df[id_column].duplicated(keep=False)
        add_rejections(name, df, duplicate_mask, "Duplicate ID")

    # Product price checks
    product_prices = pd.to_numeric(products["price"], errors="coerce")
    invalid_prices = product_prices.isna() | (product_prices <= 0)
    add_rejections(
        "products", products, invalid_prices, "Invalid product price"
    )

    # Order quantity checks
    order_quantities = pd.to_numeric(orders["quantity"], errors="coerce")
    invalid_quantities = (
        order_quantities.isna() | (order_quantities <= 0)
    )
    add_rejections(
        "orders", orders, invalid_quantities, "Invalid order quantity"
    )

    # Order date checks
    parsed_dates = pd.to_datetime(orders["order_date"], errors="coerce")
    invalid_dates = parsed_dates.isna()
    add_rejections(
        "orders", orders, invalid_dates, "Invalid order date"
    )

    # Foreign-key checks
    invalid_customers = ~orders["customer_id"].isin(customers["customer_id"])
    invalid_products = ~orders["product_id"].isin(products["product_id"])

    add_rejections(
        "orders", orders, invalid_customers,
        "Invalid customer reference"
    )
    add_rejections(
        "orders", orders, invalid_products,
        "Invalid product reference"
    )

    # Step 3: Save rejected records
    total_rejected = 0

    for name, rejected_parts in rejected_records.items():
        rejected_df = pd.concat(rejected_parts, ignore_index=True)

        # A record can fail multiple checks; combine its reasons
        group_columns = [
            column for column in rejected_df.columns
            if column not in ["reject_reason"]
        ]

        rejected_df = (
            rejected_df.groupby(group_columns, dropna=False, sort=False)
            ["reject_reason"]
            .agg("; ".join)
            .reset_index()
        )

        rejected_df = rejected_df.drop(columns=["_source_row"])
        output_path = quarantine_folder / f"rejected_{name}.csv"
        rejected_df.to_csv(output_path, index=False)

        total_rejected += len(rejected_df)
        print(f"{name}: {len(rejected_df)} rejected records")
        print(f"Saved to: {output_path}")

    # Step 4: Final result
    print("\nValidation Summary")
    print("------------------")
    print(f"Datasets checked: {len(datasets)}")
    print(f"Rejected records: {total_rejected}")

    if errors or total_rejected > 0:
        print("\nVALIDATION FAILED")
        for error in errors:
            print("-", error)
        return False

    print("\nVALIDATION PASSED")
    print("All data quality checks passed.")
    return True


if __name__ == "__main__":
    validate_data()
