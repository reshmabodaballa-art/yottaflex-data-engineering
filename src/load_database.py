
import sqlite3
import pandas as pd
import time
from pathlib import Path


def load_data():
    start_time = time.perf_counter()
    data_folder = Path("data")

    customers = pd.read_csv(data_folder / "customers.csv")
    products = pd.read_csv(data_folder / "products.csv")
    orders = pd.read_csv(data_folder / "orders.csv")

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

        # Check whether existing tables have primary keys
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
            """)

            connection.executemany(
                "INSERT OR IGNORE INTO customers VALUES (?, ?, ?)",
                customers.itertuples(index=False, name=None)
            )

            connection.executemany(
                "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)",
                products.itertuples(index=False, name=None)
            )

            connection.executemany(
                "INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?)",
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
    load_data()
