
import pandas as pd
import random
import argparse
from pathlib import Path


def generate_products(num_products=100, seed=42):

    if num_products < 0:
        raise ValueError("Invalid number of products.")

    rng = random.Random(seed)

    products = []

    categories = [
        "Electronics",
        "Clothing",
        "Furniture",
        "Books",
        "Groceries"
    ]

    for product_id in range(1, num_products + 1):
        products.append({
            "product_id": product_id,
            "product_name": f"Product_{product_id}",
            "category": rng.choice(categories),
            "price": round(rng.uniform(100, 5000), 2)
        })

    return pd.DataFrame(products)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--num-products", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    products = generate_products(
        num_products=args.num_products,
        seed=args.seed
    )

    output_folder = Path("data")
    output_folder.mkdir(exist_ok=True)

    products.to_csv(output_folder / "products.csv", index=False)

    print(f"Successfully generated {len(products)} products!")
    print(products.head())
