
import pandas as pd
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta


def generate_orders(
    num_orders=1000,
    num_customers=10,
    num_products=100,
    seed=42
):
    if num_orders < 0 or num_customers <= 0 or num_products <= 0:
        raise ValueError("Invalid dataset size.")

    rng = random.Random(seed)
    orders = []
    start_date = datetime(2026, 1, 1)

    for order_id in range(1, num_orders + 1):
        order_date = start_date + timedelta(
            days=rng.randint(0, 300)
        )

        orders.append({
            "order_id": order_id,
            "customer_id": rng.randint(1, num_customers),
            "product_id": rng.randint(1, num_products),
            "quantity": rng.randint(1, 5),
            "order_date": order_date.strftime("%Y-%m-%d")
        })

    return pd.DataFrame(orders)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--num-orders", type=int, default=1000)
    parser.add_argument("--num-customers", type=int, default=10)
    parser.add_argument("--num-products", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    orders = generate_orders(
        num_orders=args.num_orders,
        num_customers=args.num_customers,
        num_products=args.num_products,
        seed=args.seed
    )

    output_folder = Path("data")
    output_folder.mkdir(exist_ok=True)

    orders.to_csv(output_folder / "orders.csv", index=False)

    print(f"Successfully generated {len(orders)} orders!")
    print(orders.head())
