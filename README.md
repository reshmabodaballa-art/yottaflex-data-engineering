# YottaFlex Data Engineering Challenge

## 1. Project Overview

This project implements a local data engineering pipeline using Python and SQLite. It processes customer, product, and order data, performs data validation, loads records into a database, generates sales analysis, and produces reconciliation reports.

The project focuses on data quality, reliable processing, database idempotency, error recovery, operational monitoring, and performance optimization.

## 2. Technologies Used

- Python
- SQLite
- Pandas
- SQL
- Pytest
- Git and GitHub

## 3. Project Structure

```text
yottaflex-data-engineering/
│
├── data/
│   ├── customers.csv
│   ├── orders.csv
│   ├── products.csv
│   └── test_data/
│       └── bad_products.csv
│
├── reports/
│   ├── automated_test_report.txt
│   ├── bad_data_test_report.txt
│   ├── customer_generator_test_report.txt
│   ├── data_generator_test_report.txt
│   ├── idempotency_report.txt
│   ├── performance_report.txt
│   ├── pipeline.log
│   ├── pipeline_execution_report.txt
│   ├── pipeline_runs.csv
│   ├── product_generator_test_report.txt
│   ├── reconciliation_report.csv
│   ├── sales_analysis.csv
│   └── validation_report.txt
│
├── src/
│   ├── __init__.py
│   ├── checkpoint_manager.py
│   ├── generate_data.py
│   ├── generate_orders.py
│   ├── generate_products.py
│   ├── load_database.py
│   ├── performance_benchmark.py
│   ├── reconciliation.py
│   ├── run_pipeline.py
│   ├── sales_analysis.py
│   └── validate_data.py
│
├── tests/
│   ├── test_checkpoint_manager.py
│   ├── test_data_generator.py
│   ├── test_data_quality.py
│   ├── test_idempotency.py
│   └── test_pipeline_operations.py
│
├── .gitignore
├── requirements.txt
├── PROMPT_HISTORY.txt
└── README.md
```

## 4. Setup and Execution

### Prerequisites

- Python 3.10 or later
- Git

### Clone the repository

```bash
git clone https://github.com/reshmabodaballa-art/yottaflex-data-engineering.git
cd yottaflex-data-engineering
```

### Create and activate a virtual environment (Windows)

```cmd
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```cmd
pip install -r requirements.txt
```

### Run the pipeline

```cmd
python src\run_pipeline.py
```

### Run automated tests

```cmd
pytest -v
```

The project was tested from a fresh GitHub clone. The pipeline executed successfully, and all 35 automated tests passed.

## 5. Pipeline Workflow

The pipeline follows these steps:

1. Generate or read customer, product, and order CSV files.
2. Validate input data and required fields.
3. Identify invalid and duplicate records.
4. Load valid records into SQLite.
5. Generate sales analysis.
6. Perform data reconciliation.
7. Record pipeline execution details.
8. Generate reports.

## 6. Data Quality and Validation

The validation process checks:

- Required columns and schema.
- Missing required values.
- Invalid data formats.
- Duplicate primary keys.
- Invalid foreign key references.
- Malformed CSV files.

Invalid records are handled separately from valid records to protect the database from incorrect data.

The pipeline also handles empty input batches and unexpected schema changes.

## 7. Database Design

SQLite is used to store the processed data.

The database contains customer, product, and order information with primary key and foreign key relationships.

Database transactions help maintain data consistency during loading and processing.

## 8. Idempotency

The pipeline uses database operations designed to prevent duplicate records when the same input data is processed again.

Database constraints and conflict-handling logic help maintain consistency across repeated executions.

SHA-256 input fingerprinting and stage-level checkpoints help identify previously processed input and completed pipeline stages.

## 9. Error Handling and Retry

The pipeline includes error handling for invalid input and database operations.

Database transactions support rollback when processing fails. Transient SQLite database errors are handled using retry logic.

A failed pipeline can resume from the last successfully completed stage when the corresponding checkpoint is available.

## 10. Sales Analysis

The pipeline generates sales analysis using customer, product, and order data.

The analysis includes product and sales-related summaries and is saved as a CSV report.

## 11. Data Reconciliation

The pipeline generates reconciliation results to compare processed data and expected totals.

The reconciliation report includes checks for:

- Customer record counts.
- Product record counts.
- Order record counts.
- Total sales amount.

## 12. Automated Testing Results

The project includes automated tests for data quality, database idempotency, checkpoint management, and pipeline operations.

**Test execution command:**

```bash
pytest -v
```

**Verified result: 35 tests passed, 0 failed.**

The test suite covers:

- Checkpoint fingerprint generation and recovery.
- Synthetic data generation and reproducibility.
- Data quality and validation.
- Database idempotency and transaction rollback.
- Retry handling and operational metrics.
- Historical backfill and date validation.
- Late-arriving orders and corrected records.
- Unexpected schema changes.
- Malformed CSV files.
- Empty input batches.
- Missing required values.
- Invalid foreign key references.
- Out-of-order dates.
- Duplicate primary key quarantine.

## 13. Pipeline Execution and Reconciliation Results

The pipeline was executed successfully from a fresh clone of the public GitHub repository.

**Latest verified fresh-clone execution:**

- Run ID: `0cb641a4-6875-4318-8093-50a667f4dec0`
- Customers processed: 10
- Products processed: 100
- Orders processed: 100,000
- Rejected records: 0
- Total sales: 779,133,939.72
- Reconciliation: All 4 checks passed.
- Pipeline status: SUCCESS

Pipeline execution details are stored in `reports/pipeline_runs.csv`.

## 14. Checkpoints, Recovery, and Design Decisions

The project implements SHA-256 input fingerprinting and stage-level checkpoints for:

- Data validation.
- Database loading.
- Sales analysis.
- Data reconciliation.

Completed stages can be skipped when the same input is processed again.

The database supports historical order loading, late-arriving orders, and updates to corrected records.

The loader supports historical order-date filtering. However, date-range backfill parameters are not fully exposed through the complete pipeline interface.

Checkpoint fingerprints are based on source CSV inputs rather than individual backfill date ranges.

## 15. Output Files

The pipeline generates the following reports:

- `sales_analysis.csv` – Sales analysis results.
- `reconciliation_report.csv` – Data reconciliation results.
- `pipeline_runs.csv` – Pipeline execution history.
- `pipeline_execution_report.txt` – Pipeline execution summary.
- `pipeline.log` – Pipeline execution log.
- `automated_test_report.txt` – Automated testing results.
- `performance_report.txt` – Performance benchmark results.
- Additional validation and data-generator test reports.

## 16. Performance Benchmark

A performance benchmark compares a baseline SQL JOIN and GROUP BY query with a precomputed summary-table read.

**Benchmark results:**

- Baseline query median: 0.080874 seconds.
- Summary refresh: 0.082971 seconds.
- Optimized read: 0.000118 seconds.
- Reported read speedup: 687.71x.
- Reported read-time reduction: 99.85%.
- Result equivalence: PASS.

The benchmark demonstrates faster repeated reads using a precomputed summary. The summary must be refreshed when the underlying order or price data changes.

These results represent a local benchmark and may vary with hardware, database size, and workload.

## 17. Limitations and Future Improvements

The current implementation is designed as a local Python and SQLite solution.

Current limitations include:

- The complete pipeline does not expose date-range backfill parameters.
- Checkpoint fingerprints are based on source CSV files, not backfill date ranges.
- The solution does not include a production cloud orchestration platform.
- Performance results are based on a local benchmark.

Potential future improvements include:

- Cloud-based storage and orchestration.
- Integration with Apache Airflow or similar workflow tools.
- Advanced pipeline monitoring and alerting.
- Improved scalability for larger production workloads.
- More detailed row-level reconciliation and audit dashboards.

## 18. AI Assistance Disclosure

ChatGPT (OpenAI) was used as an AI assistance tool during project development.

AI assistance was used for:

- Understanding the challenge requirements.
- Planning the pipeline structure.
- Coding guidance and debugging.
- Improving validation and automated tests.
- Reviewing error handling and recovery approaches.
- Preparing project documentation.

**My contribution and verification:**

I reviewed the suggested code, worked through implementation and debugging, executed the pipeline, checked the generated outputs, and ran the automated test suite.

The project was tested from a fresh GitHub clone, with 35 automated tests passing.

The file `PROMPT_HISTORY.txt` documents the AI assistance used during development. Its current entries are summaries of the prompts rather than a complete verbatim transcript of every prompt.

## 19. Author

**Reshma Bodaballa**

B.Tech – Computer Science and Engineering