
import logging
import time
from datetime import datetime
from pathlib import Path

from validate_data import validate_data
from load_database import load_data
from sales_analysis import sales_analysis


# Create reports folder
Path("reports").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="reports/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)


def run_pipeline():
    start_time = time.perf_counter()
    start_datetime = datetime.now()

    print("=" * 50)
    print("YOTTAFLEX AI - DATA PIPELINE")
    print("=" * 50)

    logging.info("Pipeline started.")

    try:
        print("\nSTEP 1: DATA VALIDATION")
        logging.info("Data validation started.")

        validation_passed = validate_data()

        if not validation_passed:
            print("\nPipeline stopped: Data validation failed.")
            logging.error("Pipeline stopped: Validation failed.")
            return False

        logging.info("Data validation passed.")

        print("\nSTEP 2: DATABASE LOADING")
        load_data()
        logging.info("Database loading completed.")

        print("\nSTEP 3: SALES ANALYSIS")
        sales_analysis()
        logging.info("Sales analysis completed.")

        elapsed_time = time.perf_counter() - start_time

        print("\n" + "=" * 50)
        print("DATA PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)

        print(f"Total execution time: {elapsed_time:.4f} seconds")

        logging.info(
            "Pipeline completed successfully in %.4f seconds.",
            elapsed_time
        )

        return True

    except Exception:
        logging.exception("Pipeline failed due to an unexpected error.")
        print("\nPipeline failed. Check reports/pipeline.log for details.")
        return False


if __name__ == "__main__":
    run_pipeline()
