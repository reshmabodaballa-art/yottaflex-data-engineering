import sqlite3
import pandas as pd
from pathlib import Path


def reconcile_data():
    data_folder = Path("data")
    report_folder = Path("reports")
    report_folder.mkdir(exist_ok=True)

    # Read source CSV files
    customers = pd.read_csv(data_folder / "customers.csv")
    products = pd.read_csv(data_folder / "products.csv")
    orders = pd.read_csv(data_folder / "orders.csv")

    # Calculate expected source totals
    source_counts = {
        "customers": len(customers),
        "products": len(products),
        "orders": len(orders)
    }

    source_sales = orders.merge(
        products[["product_id", "price"]],
        on="product_id",
        how="inner"
    )

    expected_sales = (
        source_sales["quantity"] * source_sales["price"]
    ).sum()

    # Read database totals
    connection = sqlite3.connect("yottaflex.db")

    try:
        database_counts = {}

        for table in ["customers", "products", "orders"]:
            database_counts[table] = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

        database_sales = connection.execute("""
            SELECT SUM(o.quantity * p.price)
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
        """).fetchone()[0]

    finally:
        connection.close()

    # Compare source and database values
    results = []

    for table in ["customers", "products", "orders"]:
        results.append({
            "check": f"{table}_count",
            "source_value": source_counts[table],
            "database_value": database_counts[table],
            "status": (
                "PASS"
                if source_counts[table] == database_counts[table]
                else "FAIL"
            )
        })

    results.append({
        "check": "total_sales",
        "source_value": expected_sales,
        "database_value": database_sales or 0,
        "status": (
            "PASS"
            if abs(expected_sales - (database_sales or 0)) < 0.01
            else "FAIL"
        )
    })

    report = pd.DataFrame(results)

    report.to_csv(
        report_folder / "reconciliation_report.csv",
        index=False
    )

    print("\nDATA RECONCILIATION REPORT")
    print("--------------------------")
    print(report.to_string(index=False))

    if (report["status"] == "PASS").all():
        print("\nRECONCILIATION PASSED")
        return True

    print("\nRECONCILIATION FAILED")
    return False


if __name__ == "__main__":
    reconcile_data()