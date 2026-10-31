

\# YottaFlex AI - Data Engineering Pipeline



\## Project Overview



This project implements an end-to-end data engineering pipeline using Python, Pandas, SQLite, and SQL.



The pipeline generates synthetic customer, product, and order datasets, validates data quality, loads the datasets into a relational database, and performs sales analysis.



The project focuses on data quality, reproducibility, database integrity, automated testing, and safe pipeline reruns.



\## Technologies Used



\- Python

\- Pandas

\- SQLite

\- SQL

\- Pytest

\- Git





\## Project Structure



```text

yottaflex-data-engineering/

│

├── data/

│   ├── customers.csv

│   ├── products.csv

│   ├── orders.csv

│   └── test\_data/

│

├── src/

│   ├── generate\_data.py

│   ├── generate\_products.py

│   ├── generate\_orders.py

│   ├── validate\_data.py

│   ├── load\_database.py

│   ├── sales\_analysis.py

│   └── run\_pipeline.py

│

├── tests/

│   ├── test\_data\_quality.py

│   └── test\_idempotency.py

│

├── reports/

│   ├── validation\_report.txt

│   ├── automated\_test\_report.txt

│   ├── performance\_report.txt

│   ├── pipeline\_execution\_report.txt

│   ├── pipeline.log

│   ├── sales\_analysis.csv

│   ├── bad\_data\_test\_report.txt

│   ├── idempotency\_report.txt

│   └── data\_generator\_test\_report.txt     

│

├── requirements.txt

├── README.md

└── yottaflex.db

```



\## Pipeline Workflow



The pipeline executes the following stages:



1\. \*\*Data Generation\*\*

&#x20;  - Generate synthetic customer data.

&#x20;  - Generate synthetic product data.

&#x20;  - Generate synthetic order data.

&#x20;  - Support configurable dataset sizes and fixed random seeds.



2\. \*\*Data Validation\*\*

&#x20;  - Check required columns.

&#x20;  - Check missing values.

&#x20;  - Detect duplicate IDs.

&#x20;  - Validate product prices and order quantities.

&#x20;  - Validate order dates and foreign-key references.



3\. \*\*Database Loading\*\*

&#x20;  - Load validated data into SQLite.

&#x20;  - Use primary keys and foreign keys.

&#x20;  - Prevent duplicate records during reruns.



4\. \*\*Sales Analysis\*\*

&#x20;  - Join orders with products.

&#x20;  - Calculate sales by product category.

&#x20;  - Export results to `reports/sales\_analysis.csv`.



\## System Architecture



The project follows a simple ETL (Extract, Transform, Load) architecture.



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
     Output Reports


\## Installation and Execution



\### 1. Clone the repository



```bash

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd yottaflex-data-engineering

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



\### 3. Activate the environment



Windows:



```bash

venv\\Scripts\\activate

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\### 5. Run the complete pipeline



```bash

python src/run\_pipeline.py

```



\### 6. Run automated tests



```bash

pytest tests/ -v

```



\### Synthetic Data Generation



The generators support configurable dataset sizes and random seeds.



Examples:



```bash

python src/generate\_data.py --num-customers 10 --seed 42

python src/generate\_products.py --num-products 100 --seed 42

python src/generate\_orders.py --num-orders 100000 --num-customers 10 --num-products 100 --seed 42

```



\*\*Note:\*\* Run the generators with matching customer and product counts before regenerating orders, because orders reference customer and product IDs.





\## Dataset Details



The current project uses reproducible synthetic datasets.



| Dataset | Number of Records |

|---|---:|

| Customers | 10 |

| Products | 100 |

| Orders | 100,000 |



\## Data Dictionary



\### Customers Dataset



| Column | Data Type | Description |

|---|---|---|

| customer\_id | Integer | Unique customer ID |

| customer\_name | Text | Customer name |

| city | Text | Customer city |



\### Products Dataset



| Column | Data Type | Description |

|---|---|---|

| product\_id | Integer | Unique product ID |

| product\_name | Text | Product name |

| category | Text | Product category |

| price | Float | Product price |



\### Orders Dataset



| Column | Data Type | Description |

|---|---|---|

| order\_id | Integer | Unique order ID |

| customer\_id | Integer | Customer ID linked to customers |

| product\_id | Integer | Product ID linked to products |

| quantity | Integer | Number of items ordered |

| order\_date | Date | Date of the order |



\## Sample Input and Output



\### Sample Input



The project includes a test file named `bad\_products.csv` to check invalid product records.



| product\_id | product\_name | category | price |

|---|---|---|---:|

| 101 | Mobile | Electronics | 15000 |

| 102 | Laptop | Electronics | -500 |

| 103 | Book | Books | 0 |

| 104 | Chair | Furniture | 2500 |

| 101 | Duplicate\_Mobile | Electronics | 12000 |



\### Sample Validation Results



\- Total records: 5

\- Valid records: 1

\- Invalid records: 4

\- Issues detected: Negative price, zero price, and duplicate product ID.



\## Testing Results



Automated testing is performed using Pytest.



\- Total tests: 7

\- Passed: 7

\- Failed: 0

\- Latest recorded execution time: 3.09 seconds



Tests cover:

\- Negative and zero product prices.

\- Duplicate product IDs.

\- Empty datasets.

\- Missing product names.

\- Invalid order quantities.

\- Invalid order dates.

\- Database loading idempotency.



\## Pipeline Execution



The complete pipeline was executed successfully twice.



\- Data validation: Passed

\- Database loading: Passed

\- Sales analysis: Passed

\- Database record counts remained unchanged after rerunning.



\## Output Files



\- `yottaflex.db` - SQLite database.

\- `reports/sales\_analysis.csv` - Sales analysis results.

\- `reports/validation\_report.txt` - Data validation results.

\- `reports/automated\_test\_report.txt` - Automated test results.

\- `reports/performance\_report.txt` - SQL performance comparison.

\- `reports/pipeline.log` - Automatic pipeline execution logs, status, and errors.

\- `reports/pipeline\_execution\_report.txt` - Pipeline execution and rerun results.



\## Design Decisions and Trade-offs



\- \*\*SQLite:\*\* Selected as a lightweight relational database for storing and querying project data.

\- \*\*Pandas:\*\* Used for CSV processing, data validation, and report generation.

\- \*\*Primary and Foreign Keys:\*\* Used to maintain database relationships and data integrity.

\- \*\*Fixed Random Seed:\*\* Used to generate reproducible synthetic datasets.

\- \*\*INSERT OR IGNORE:\*\* Used to prevent duplicate primary-key records during repeated database loads.

\- \*\*Pytest:\*\* Used to automate data-quality and idempotency tests.



\## Current Limitations and Future Improvements



\- Add automated rejection files for invalid records.

\- Enhance run-status tracking with persistent execution metadata and row counts.

\- Improve handling of partial failures and retries.

\- Add schema-change detection and stricter data-type validation.

\- Expand automated tests for foreign-key errors and malformed input files.

\- Explore and measure further performance optimizations.



\## Author



Developed as an individual data engineering project for the YottaFlex AI assessment.



