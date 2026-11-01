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
    # Read source primary keys for record-level reconciliation
    source_ids = {
        "customers": set(customers["customer_id"]),
        "products": set(products["product_id"]),
        "orders": set(orders["order_id"])
    }
    # Check orders referencing missing customers or products
    source_orphan_customers = (
        ~orders["customer_id"].isin(customers["customer_id"])
    ).sum()

    source_orphan_products = (
        ~orders["product_id"].isin(products["product_id"])
    ).sum()
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
        # Read database primary keys for record-level reconciliation
        database_ids = {}

        for table, id_column in [
            ("customers", "customer_id"),
            ("products", "product_id"),
            ("orders", "order_id")
        ]:
            database_ids[table] = {
                row[0] for row in connection.execute(
                    f"SELECT {id_column} FROM {table}"
                ).fetchall()
            }
        # Check duplicate primary keys in database
        database_duplicates = {}

        for table, id_column in [
            ("customers", "customer_id"),
            ("products", "product_id"),
            ("orders", "order_id")
        ]:
            database_duplicates[table] = connection.execute(
                f"""
                SELECT COUNT(*)
                FROM (
                    SELECT {id_column}
                    FROM {table}
                    GROUP BY {id_column}
                    HAVING COUNT(*) > 1
                )
                """
            ).fetchone()[0]
        # Read complete database records for value comparison
        database_records = {
            "customers": pd.read_sql_query(
                "SELECT * FROM customers", connection
            ),
            "products": pd.read_sql_query(
                "SELECT * FROM products", connection
            ),
            "orders": pd.read_sql_query(
                "SELECT * FROM orders", connection
            )
        }
        # Check database orders referencing missing customers or products
        database_orphan_customers = connection.execute("""
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """).fetchone()[0]

        database_orphan_products = connection.execute("""
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.product_id
            WHERE p.product_id IS NULL
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
    # Check for missing and extra records
    for table in ["customers", "products", "orders"]:
        missing_ids = source_ids[table] - database_ids[table]
        extra_ids = database_ids[table] - source_ids[table]

        results.append({
            "check": f"{table}_missing_records",
            "source_value": 0,
            "database_value": len(missing_ids),
            "status": "PASS" if len(missing_ids) == 0 else "FAIL"
        })

        results.append({
            "check": f"{table}_extra_records",
            "source_value": 0,
            "database_value": len(extra_ids),
            "status": "PASS" if len(extra_ids) == 0 else "FAIL"
        })
    # Check invalid customer and product references
    results.append({
        "check": "orphan_customer_references",
        "source_value": source_orphan_customers,
        "database_value": database_orphan_customers,
        "status": (
            "PASS"
            if source_orphan_customers == 0
            and database_orphan_customers == 0
            else "FAIL"
        )
    })

    results.append({
        "check": "orphan_product_references",
        "source_value": source_orphan_products,
        "database_value": database_orphan_products,
        "status": (
            "PASS"
            if source_orphan_products == 0
            and database_orphan_products == 0
            else "FAIL"
        )
    })
    # Check duplicate primary keys in database
    for table in ["customers", "products", "orders"]:
        results.append({
            "check": f"{table}_duplicate_ids",
            "source_value": 0,
            "database_value": database_duplicates[table],
            "status": (
                "PASS"
                if database_duplicates[table] == 0
                else "FAIL"
            )
        })
    # Compare actual source and database record values
    primary_keys = {
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id"
    }

    for table, primary_key in primary_keys.items():
        source_df = customers if table == "customers" else (
            products if table == "products" else orders
        )

        database_df = database_records[table]

        comparison = source_df.merge(
            database_df,
            on=primary_key,
            how="inner",
            suffixes=("_source", "_database")
        )

        columns_to_compare = [
            column for column in source_df.columns
            if column != primary_key
        ]

        mismatch_mask = pd.Series(
            False, index=comparison.index
        )

        for column in columns_to_compare:
            source_values = comparison[f"{column}_source"]
            database_values = comparison[f"{column}_database"]

            same_values = (
                source_values.eq(database_values)
                | (
                    source_values.isna()
                    & database_values.isna()
                )
            )

            mismatch_mask |= ~same_values

        mismatch_count = int(mismatch_mask.sum())

        results.append({
            "check": f"{table}_value_mismatches",
            "source_value": 0,
            "database_value": mismatch_count,
            "status": "PASS" if mismatch_count == 0 else "FAIL"
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
        report_folder / "reconciliation_report.pending.csv",
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