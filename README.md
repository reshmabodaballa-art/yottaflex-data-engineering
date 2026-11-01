

# YottaFlex Data Engineering Challenge

## 1. Project Overview

This project implements a data engineering pipeline using Python and SQLite. It processes customer, product, and order data, performs data validation, loads records into a database, generates sales analysis, and produces reconciliation reports.

The project focuses on data quality, reliable processing, database idempotency, operational monitoring, and performance optimization.

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
│   ├── products.csv
│   └── orders.csv
│
├── docs/
│   ├── architecture.md
│   └── data_dictionary.md
│
├── reports/
│   ├── automated_test_report.txt
│   ├── performance_report.txt
│   ├── pipeline_execution_report.txt
│   ├── pipeline_runs.csv
│   ├── reconciliation_report.csv
│   └── sales_analysis.csv
│
├── src/
│   ├── __init__.py
│   ├── checkpoint_manager.py
│   ├── generate_data.py
│   ├── load_database.py
│   ├── run_pipeline.py
│   ├── validate_data.py
│   ├── sales_analysis.py
│   ├── reconciliation.py
│   └── performance_benchmark.py
│
├── tests/
│   ├── test_checkpoint_manager.py
│   ├── test_data_generator.py
│   ├── test_data_quality.py
│   ├── test_idempotency.py
│   └── test_pipeline_operations.py
│
├── requirements.txt
└── README.md
```

## 4. Pipeline Workflow

The pipeline follows these steps:

1. Read customer, product, and order CSV files.
2. Validate input data and required fields.
3. Identify invalid and duplicate records.
4. Load valid records into SQLite.
5. Generate sales analysis.
6. Perform data reconciliation.
7. Record pipeline execution details.
8. Generate reports.

## 5. Data Quality and Validation

The validation process checks:

- Required columns and schema.
- Missing required values.
- Invalid data formats.
- Duplicate primary keys.
- Invalid foreign key references.
- Malformed CSV files.

Invalid records are handled separately from valid records to protect the database from incorrect data.

## 6. Database Design

SQLite is used to store the processed data.

The database contains customer, product, and order information with primary key and foreign key relationships.

The pipeline uses database transactions to maintain data consistency.

## 7. Idempotency

The pipeline uses database operations designed to prevent duplicate records when the same input data is processed again.

Database constraints and conflict-handling logic help maintain consistency across repeated executions.

## 8. Error Handling and Retry

The pipeline includes error handling for invalid input and database operations.

Database transactions support rollback when processing fails. Transient SQLite database errors are handled using retry logic.

## 9. Sales Analysis

The pipeline generates sales analysis using customer, product, and order data.

The analysis includes product and sales-related summaries and is saved as a CSV report.

## 10. Data Reconciliation

The pipeline generates reconciliation results to compare processed data and expected totals.

The reconciliation report includes checks for:

- Customer record counts.
- Product record counts.
- Order record counts.
- Total sales amount.

## 11. Automated Testing Results

The project includes automated tests for data quality, database idempotency, and pipeline operations.

**Test execution command:**

```bash
pytest -v
```

**Result:** 35 tests passed, 0 failed.

The test suite covers:
- Checkpoint fingerprint generation and recovery.
- Synthetic data generation and reproducibility.
- Data quality and validation.
- Database idempotency and transaction rollback.
- Retry handling and operational metrics.
- Historical backfill and date validation.
- Late-arriving orders and corrected records.

Additional test scenarios include:

- Unexpected schema changes.
- Malformed CSV files.
- Empty input batches.
- Missing required values.
- Invalid foreign key references.
- Out-of-order dates.
- Transaction rollback and retry.
- Transient database errors.
- Pipeline run tracking and operational metrics.
- Duplicate primary key quarantine.

## 12. Pipeline Execution and Reconciliation Results

The pipeline was executed successfully.

**Latest successful execution:**

- Run ID: `a133a8ad-5373-4df3-93c8-6a95d12a0115`
- Customers processed: 10
- Products processed: 100
- Orders processed: 100,000
- Rejected records: 0
- Total sales: 779,133,939.72
- Reconciliation: All 4 checks passed.

Pipeline execution details are stored in `reports/pipeline_runs.csv`.

## 13. Idempotency, Retry, and Design Decisions

The pipeline uses database transactions to protect data consistency during processing.

If an invalid operation occurs, the transaction can be rolled back. Retry logic is also included for transient SQLite database errors.

Pipeline execution details are recorded using a run ID and operational metrics.

The project implements SHA-256 input fingerprinting and stage-level checkpoints for validation, database loading, sales analysis, and reconciliation.

Completed stages are skipped when the same input is processed again. The database supports historical order backfills, late-arriving orders, and updates to corrected records.

A failed pipeline can resume from the last successfully completed stage.

## 14. Output Files

The pipeline generates the following reports:

- `sales_analysis.csv` – Sales analysis results.
- `reconciliation_report.csv` – Data reconciliation results.
- `pipeline_runs.csv` – Pipeline execution history.
- `pipeline_execution_report.txt` – Pipeline execution summary.
- `automated_test_report.txt` – Automated testing results.
- `performance_report.txt` – Performance benchmark results.

## 15. Performance Benchmark

A performance benchmark compares a baseline SQL JOIN and GROUP BY query with a precomputed summary-table read.

**Benchmark results:**

- Baseline query median: 0.080874 seconds.
- Summary refresh: 0.082971 seconds.
- Optimized read: 0.000118 seconds.
- Reported read speedup: 687.71x.
- Reported read-time reduction: 99.85%.
- Result equivalence: PASS.

The benchmark demonstrates faster repeated reads using a precomputed summary. The summary must be refreshed when the underlying order or price data changes.

## 16. Limitations and Future Improvements

The current implementation is designed as a local Python and SQLite solution.

Potential future improvements include:

- Cloud-based storage and orchestration.
- Integration with Apache Airflow or similar workflow tools.
- Advanced pipeline monitoring and alerting.
- Improved scalability for larger production workloads.
- More detailed row-level reconciliation and audit dashboards.

## 17. Author

**Reshma Bodaballa**

B.Tech – Computer Science and Engineering

