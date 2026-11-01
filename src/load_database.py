
import sqlite3
import pandas as pd
import time
import argparse
from pathlib import Path
import json
import uuid
from datetime import datetime, timezone
def save_record_history(
    connection, entity_type, dataframe, primary_key,
    columns, source_file, run_id
):
    timestamp = datetime.now(timezone.utc).isoformat()

    for _, row in dataframe.iterrows():
        record = {
            column: row[column].item()
            if hasattr(row[column], "item")
            else row[column]
            for column in columns
        }

        record_id = str(record[primary_key])

        existing = connection.execute(
            f"SELECT {', '.join(columns)} FROM {entity_type} "
            f"WHERE {primary_key} = ?",
            (record[primary_key],)
        ).fetchone()

        new_values = json.dumps(record, sort_keys=True)

        if existing is None:
            operation = "INSERT"
            previous_values = None
        else:
            old_record = dict(zip(columns, existing))

            if old_record == record:
                continue

            operation = "UPDATE"
            previous_values = json.dumps(
                old_record, sort_keys=True
            )

        connection.execute(
            """
            INSERT INTO source_record_history (
                entity_type, record_id, source_file, run_id,
                operation, previous_values, new_values, ingested_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entity_type, record_id, source_file, run_id,
                operation, previous_values, new_values, timestamp
            )
        )
def load_data(start_date=None, end_date=None):
    start_time = time.perf_counter()
    run_id = str(uuid.uuid4())
    data_folder = Path("data")

    customers = pd.read_csv(data_folder / "customers.csv")
    products = pd.read_csv(data_folder / "products.csv")
    orders = pd.read_csv(data_folder / "orders.csv")

    # Validate and apply an optional historical date range.
    if start_date or end_date:
        orders["order_date"] = pd.to_datetime(
            orders["order_date"], errors="raise"
        ).dt.strftime("%Y-%m-%d")

        if start_date:
            pd.to_datetime(start_date, format="%Y-%m-%d", errors="raise")
            orders = orders[orders["order_date"] >= start_date]

        if end_date:
            pd.to_datetime(end_date, format="%Y-%m-%d", errors="raise")
            orders = orders[orders["order_date"] <= end_date]

        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date.")

        print(
            f"Historical backfill range: "
            f"{start_date or 'beginning'} to {end_date or 'latest'}"
        )

    connection = sqlite3.connect("yottaflex.db")

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        required_tables = {
            "customers": "customer_id",
            "products": "product_id",
            "orders": "order_id"
        }

        existing_tables = {
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        needs_rebuild = existing_tables.intersection(required_tables)

        if needs_rebuild:
            needs_rebuild = (
                existing_tables.intersection(required_tables)
                != set(required_tables)
            )

            for table, primary_key in required_tables.items():
                if table in existing_tables:
                    info = connection.execute(
                        f"PRAGMA table_info({table})"
                    ).fetchall()

                    has_primary_key = any(
                        row[1] == primary_key and row[5] > 0
                        for row in info
                    )


                    if not has_primary_key:
                        needs_rebuild = True
            
        with connection:
            if needs_rebuild:
                connection.execute("DROP TABLE IF EXISTS orders")
                connection.execute("DROP TABLE IF EXISTS products")
                connection.execute("DROP TABLE IF EXISTS customers")

            connection.executescript("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    city TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL CHECK(price > 0)
                );

                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    order_date TEXT NOT NULL,
                    FOREIGN KEY (customer_id)
                        REFERENCES customers(customer_id),
                    FOREIGN KEY (product_id)
                        REFERENCES products(product_id)
                );
               CREATE TABLE IF NOT EXISTS source_record_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    source_file TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    previous_values TEXT,
                    new_values TEXT NOT NULL,
                    ingested_at TEXT NOT NULL
                );
            """)

            save_record_history(
                connection, "customers", customers,
                "customer_id",
                ["customer_id", "customer_name", "city"],
                "customers.csv", run_id
            )
            save_record_history(
                connection, "products", products,
                "product_id",
                ["product_id", "product_name", "category", "price"],
                "products.csv", run_id
            )
            save_record_history(
                connection, "orders", orders,
                "order_id",
                ["order_id", "customer_id", "product_id", "quantity", "order_date"],
                "orders.csv", run_id
            )
            connection.executemany(
                """
                INSERT INTO customers
                (customer_id, customer_name, city)
                VALUES (?, ?, ?)
                ON CONFLICT(customer_id) DO UPDATE SET
                    customer_name = excluded.customer_name,
                    city = excluded.city
                """,
                customers.itertuples(index=False, name=None)
            )

            connection.executemany(
                """
                INSERT INTO products
                (product_id, product_name, category, price)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    product_name = excluded.product_name,
                    category = excluded.category,
                    price = excluded.price
                """,
                products.itertuples(index=False, name=None)
            )

            connection.executemany(
                """
                INSERT INTO orders
                (order_id, customer_id, product_id, quantity, order_date)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    customer_id = excluded.customer_id,
                    product_id = excluded.product_id,
                    quantity = excluded.quantity,
                    order_date = excluded.order_date
                """,
                orders.itertuples(index=False, name=None)
            )

        print("All datasets loaded successfully!")

        for table in required_tables:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count} records")

    finally:
        connection.close()

    elapsed_time = time.perf_counter() - start_time
    print(f"\nDatabase loading time: {elapsed_time:.4f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load all data or backfill orders for a date range."
    )
    parser.add_argument("--start-date", help="Start date: YYYY-MM-DD")
    parser.add_argument("--end-date", help="End date: YYYY-MM-DD")
    args = parser.parse_args()

    load_data(args.start_date, args.end_date)
