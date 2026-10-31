
import pandas as pd
import random
import argparse
from pathlib import Path


def generate_customers(num_customers=10, seed=42):

    if num_customers < 0:
        raise ValueError("Invalid number of customers.")

    rng = random.Random(seed)

    customers = []

    cities = ["Visakhapatnam", "Hyderabad", "Bengaluru"]

    for customer_id in range(1, num_customers + 1):
        customers.append({
            "customer_id": customer_id,
            "customer_name": f"Customer_{customer_id}",
            "city": rng.choice(cities)
        })

    return pd.DataFrame(customers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--num-customers", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    customers = generate_customers(
        num_customers=args.num_customers,
        seed=args.seed
    )

    output_folder = Path("data")
    output_folder.mkdir(exist_ok=True)

    customers.to_csv(output_folder / "customers.csv", index=False)

    print(f"Successfully generated {len(customers)} customers!")
    print(customers.head())
