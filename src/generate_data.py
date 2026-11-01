
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

CITIES = [
    "Hyderabad", "Visakhapatnam", "Bengaluru",
    "Chennai", "Mumbai", "Pune"
]

CATEGORIES = [
    "Electronics", "Furniture", "Clothing",
    "Books", "Home"
]


def generate_data(output_dir, customers_count, products_count,
                  orders_count, seed):

    if customers_count < 1 or products_count < 1 or orders_count < 0:
        raise ValueError(
            "Customers and products must be positive; orders cannot be negative."
        )

    rng = random.Random(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    customers = [
        {
            "customer_id": i,
            "customer_name": f"Customer_{i}",
            "city": rng.choice(CITIES)
        }
        for i in range(1, customers_count + 1)
    ]

    products = [
        {
            "product_id": i,
            "product_name": f"Product_{i}",
            "category": rng.choice(CATEGORIES),
            "price": round(rng.uniform(10, 2000), 2)
        }
        for i in range(1, products_count + 1)
    ]

    start_date = date(2025, 1, 1)
    orders = []

    for i in range(1, orders_count + 1):
        order_date = start_date + timedelta(
            days=rng.randint(0, 600)
        )

        orders.append({
            "order_id": i,
            "customer_id": rng.randint(1, customers_count),
            "product_id": rng.randint(1, products_count),
            "quantity": rng.randint(1, 10),
            "order_date": order_date.isoformat()
        })

    datasets = {
        "customers.csv": (
            customers,
            ["customer_id", "customer_name", "city"]
        ),
        "products.csv": (
            products,
            ["product_id", "product_name", "category", "price"]
        ),
        "orders.csv": (
            orders,
            ["order_id", "customer_id", "product_id",
             "quantity", "order_date"]
        )
    }

    for filename, (rows, columns) in datasets.items():
        with (output_dir / filename).open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    print("Dataset generation completed successfully.")
    print(f"Output folder: {output_dir}")
    print(f"Customers: {customers_count}")
    print(f"Products: {products_count}")
    print(f"Orders: {orders_count}")
    print(f"Random seed: {seed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate reproducible synthetic datasets."
    )

    parser.add_argument("--customers", type=int, default=10)
    parser.add_argument("--products", type=int, default=100)
    parser.add_argument("--orders", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/generated")

    args = parser.parse_args()

    generate_data(
        args.output,
        args.customers,
        args.products,
        args.orders,
        args.seed
    )
