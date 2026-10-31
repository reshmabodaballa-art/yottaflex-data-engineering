import sqlite3
import pandas as pd
from pathlib import Path


def sales_analysis():
    connection = sqlite3.connect("yottaflex.db")

    query = """
    SELECT
        p.category,
        SUM(o.quantity * p.price) AS total_sales
    FROM orders o
    JOIN products p
        ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_sales DESC;
    """

    sales_report = pd.read_sql_query(query, connection)

    print("Sales Analysis by Product Category:\n")
    print(sales_report)

    # Save report as CSV
    output_folder = Path("reports")
    output_folder.mkdir(exist_ok=True)

    sales_report.to_csv(
        output_folder / "sales_analysis.csv",
        index=False
    )

    print("\nSales report saved successfully!")

    connection.close()


if __name__ == "__main__":
    sales_analysis()