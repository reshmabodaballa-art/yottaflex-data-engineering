# YottaFlex AI – Data Engineering Pipeline

## 1. Project Overview

This project implements an end-to-end data engineering pipeline using Python, Pandas, SQLite, and SQL.

The pipeline works with synthetic customer, product, and order datasets. It validates input data, identifies invalid records, loads valid datasets into a relational database, performs sales analysis, and reconciles source data against database results.

The project focuses on data quality, reproducibility, database integrity, automated testing, safe reruns, and reporting.

## 2. Technologies Used

- Python
- Pandas
- SQLite
- SQL
- Pytest
- Git and GitHub

## 3. Project Structure

```text
yottaflex-data-engineering/
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── test_data/
│   │   └── bad_products.csv
│   └── quarantine/
│
├── src/
│   ├── generate_data.py
│   ├── generate_products.py
│   ├── generate_orders.py
│   ├── validate_data.py
│   ├── load_database.py
│   ├── sales_analysis.py
│   ├── reconciliation.py
│   └── run_pipeline.py
│
├── tests/
│   ├── test_data_quality.py
│   └── test_idempotency.py
│
├── reports/
│   ├── validation_report.txt
│   ├── automated_test_report.txt
│   ├── performance_report.txt
│   ├── pipeline_execution_report.txt
│   ├── pipeline.log
│   ├── sales_analysis.csv
│   ├── bad_data_test_report.txt
│   ├── idempotency_report.txt
│   ├── data_generator_test_report.txt
│   └── reconciliation_report.csv
│
├── requirements.txt
├── README.md
└── yottaflex.db
```

## 4. Pipeline Workflow

The pipeline executes four main stages.

### Stage 1: Data Validation

- Checks whether required CSV files and columns are available.
- Checks missing required values.
- Detects duplicate customer, product, and order IDs.
- Validates that product prices are positive.
- Validates that order quantities are positive.
- Checks order dates.
- Checks customer and product foreign-key references.
- Saves rejected records with rejection reasons in `data/quarantine/`.

**Validation policy:** The current pipeline follows a fail-fast approach. If validation errors or rejected records are found, the pipeline stops before database loading.

### Stage 2: Database Loading

- Loads validated CSV data into SQLite.
- Uses primary keys and foreign-key constraints.
- Enables foreign-key checking.
- Uses `INSERT OR IGNORE` to avoid inserting duplicate primary-key records during reruns.

### Stage 3: Sales Analysis

- Joins orders with products.
- Calculates sales using order quantity multiplied by product price.
- Groups sales by product category.
- Exports the results to `reports/sales_analysis.csv`.

### Stage 4: Data Reconciliation

- Compares source CSV record counts with database record counts.
- Compares total sales calculated from source data with database sales.
- Generates `reports/reconciliation_report.csv`.
- Reports PASS or FAIL for each reconciliation check.

## 5. System Architecture

The project follows an ETL-style workflow with a final reconciliation stage.

```text
Synthetic Data Generation
          |
          v
     CSV Input Files
          |
          v
     Data Validation
          |
          v
    SQLite Database
          |
          v
     Sales Analysis
          |
          v
   Data Reconciliation
          |
          v
      Output Reports
```

## 6. Installation and Execution

### Step 1: Clone the repository

```bash
git clone https://github.com/reshmabodaballa-art/yottaflex-data-engineering.git
cd yottaflex-data-engineering
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

### Step 3: Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the complete pipeline

```bash
python src/run_pipeline.py
```

### Step 6: Run automated tests

```bash
pytest -v
```

## 7. Synthetic Data Generation

The project includes generators for customers, products, and orders. Fixed random seeds support reproducible synthetic datasets.

Example commands:

```bash
python src/generate_data.py --num-customers 10 --seed 42

python src/generate_products.py --num-products 100 --seed 42

python src/generate_orders.py --num-orders 100000 --num-customers 10 --num-products 100 --seed 42
```

**Important:** Run generators carefully because they overwrite their corresponding CSV files. Generate matching customer and product datasets before generating orders, because orders reference customer and product IDs.

## 8. Dataset Details

The current sample datasets contain:

| Dataset | Records |
|---|---:|
| Customers | 10 |
| Products | 100 |
| Orders | 100,000 |

These are synthetic records created for testing and demonstration.

## 9. Data Dictionary

### Customers

| Column | Data Type | Description |
|---|---|---|
| customer_id | Integer | Unique customer identifier and primary key |
| customer_name | Text | Customer name |
| city | Text | Customer city |

### Products

| Column | Data Type | Description |
|---|---|---|
| product_id | Integer | Unique product identifier and primary key |
| product_name | Text | Product name |
| category | Text | Product category |
| price | Numeric | Product price; must be greater than zero |

### Orders

| Column | Data Type | Description |
|---|---|---|
| order_id | Integer | Unique order identifier and primary key |
| customer_id | Integer | Customer reference |
| product_id | Integer | Product reference |
| quantity | Integer | Number of items ordered; must be greater than zero |
| order_date | Date | Date of the order |

### Relationships

- One customer can be associated with multiple orders.
- One product can be associated with multiple orders.
- Each order references a customer and a product.
- `customer_id` and `product_id` in the orders dataset are foreign-key references.

## 10. Data Quality and Quarantine

The project includes `data/test_data/bad_products.csv` to demonstrate data-quality checks.

The sample contains five records, including negative and zero prices and a duplicate product ID.

The validation process identifies invalid records and saves them in the quarantine folder with:

- Original record information.
- Source filename.
- Rejection reason.

A record that violates multiple checks can have multiple rejection reasons.

The current validator stops the pipeline when rejected records are found; it does not load the remaining accepted records from that batch.

## 11. Testing Results

Automated tests are performed using Pytest.

Latest recorded test execution:

| Result | Count |
|---|---:|
| Total tests | 8 |
| Passed | 8 |
| Failed | 0 |

Tests cover:

- Negative and zero product prices.
- Duplicate product IDs.
- Empty datasets.
- Missing product names.
- Invalid order quantities.
- Invalid order dates.
- Saving invalid product records to quarantine.
- Database loading idempotency.

Command used:

```bash
pytest -v
```

## 12. Pipeline Execution and Reconciliation Results

The complete pipeline was executed successfully.

Latest recorded execution:

- Data validation: Passed.
- Database loading: Passed.
- Sales analysis: Passed.
- Data reconciliation: Passed.
- Total execution time: Approximately 0.4989 seconds.

Latest reconciliation results:

| Check | Source Value | Database Value | Status |
|---|---:|---:|---|
| Customers count | 10 | 10 | PASS |
| Products count | 100 | 100 | PASS |
| Orders count | 100,000 | 100,000 | PASS |
| Total sales | 779,133,939.72 | 779,133,939.72 | PASS |

Reconciliation compares row counts and aggregate sales. It does not compare every individual source record.

## 13. Idempotency and Design Decisions

- **SQLite:** Used as a lightweight relational database.
- **Pandas:** Used for CSV reading, validation, transformation, and reporting.
- **Primary and foreign keys:** Help maintain relational integrity.
- **Fixed random seed:** Supports reproducible synthetic data generation.
- **INSERT OR IGNORE:** Prevents duplicate primary-key insertions during repeated database loads.
- **Pytest:** Automates data-quality and idempotency checks.

The current loading strategy ignores records whose primary keys already exist. It does not update existing database records when their source values change. Therefore, changed source records require an explicit update or reload strategy.

## 14. Output Files

| File | Purpose |
|---|---|
| `yottaflex.db` | SQLite database |
| `reports/sales_analysis.csv` | Sales by product category |
| `reports/reconciliation_report.csv` | Source-to-database reconciliation results |
| `reports/pipeline.log` | Pipeline execution logs and errors |
| `data/quarantine/` | Rejected records and rejection reasons |
| `reports/validation_report.txt` | Validation report, if generated |
| `reports/automated_test_report.txt` | Test report, if generated |
| `reports/performance_report.txt` | Performance comparison report |
| `reports/pipeline_execution_report.txt` | Pipeline execution report |

## 15. Current Limitations and Future Improvements

- Add persistent run metadata with unique run IDs, start and end timestamps, status, and row counts.
- Improve partial-failure recovery, retries, and backfill handling.
- Add stronger schema-change detection and data-type validation.
- Expand tests for malformed files, invalid foreign keys, and additional domain-specific cases.
- Compare individual source and target records in addition to aggregate reconciliation.
- Evaluate further performance optimizations through repeatable benchmarks.

## 16. Author

Developed as an individual data engineering project for the YottaFlex AI assessment.