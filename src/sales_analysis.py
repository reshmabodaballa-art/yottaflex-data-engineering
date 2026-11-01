import sqlite3
import pandas as pd
import time
from pathlib import Path


BASELINE_QUERY = """
SELECT
    p.category,
    SUM(o.quantity * p.price) AS total_sales
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales DESC;
"""

OPTIMIZED_QUERY = """
SELECT category, total_sales
FROM category_sales_summary
ORDER BY total_sales DESC;
"""


def refresh_category_sales_summary(connection):
    """Pre-aggregate the repeated category sales workload for faster reads."""
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS category_sales_summary (
                category TEXT PRIMARY KEY,
                total_sales REAL NOT NULL
            )
        """)
        connection.execute("DELETE FROM category_sales_summary")
        connection.execute("""
            INSERT INTO category_sales_summary (category, total_sales)
            SELECT p.category, SUM(o.quantity * p.price)
            FROM orders AS o
            JOIN products AS p ON p.product_id = o.product_id
            GROUP BY p.category
        """)


def sales_analysis():
    connection = sqlite3.connect("yottaflex.db")
    try:
        refresh_category_sales_summary(connection)
        sales_report = pd.read_sql_query(OPTIMIZED_QUERY, connection)
    finally:
        connection.close()

    print("Sales Analysis by Product Category (pre-aggregated):\n")
    print(sales_report)

    output_folder = Path("reports")
    output_folder.mkdir(exist_ok=True)
    sales_report.to_csv(output_folder / "sales_analysis.csv", index=False)
    print("\nSales report saved successfully!")


if __name__ == "__main__":
    sales_analysis()
