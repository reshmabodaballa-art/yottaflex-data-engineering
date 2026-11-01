import sqlite3
import statistics
import time
from pathlib import Path

from sales_analysis import BASELINE_QUERY, OPTIMIZED_QUERY, refresh_category_sales_summary


def measure(connection, query, repetitions=25):
    connection.execute(query).fetchall()  # warm-up
    samples = []
    for _ in range(repetitions):
        started = time.perf_counter()
        rows = connection.execute(query).fetchall()
        samples.append(time.perf_counter() - started)
    return rows, statistics.median(samples)


def run_benchmark():
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    connection = sqlite3.connect("yottaflex.db")
    try:
        baseline_rows, baseline_seconds = measure(connection, BASELINE_QUERY)
        refresh_started = time.perf_counter()
        refresh_category_sales_summary(connection)
        refresh_seconds = time.perf_counter() - refresh_started
        optimized_rows, optimized_seconds = measure(connection, OPTIMIZED_QUERY)

        baseline_normalized = [(row[0], round(row[1], 2)) for row in baseline_rows]
        optimized_normalized = [(row[0], round(row[1], 2)) for row in optimized_rows]
        if baseline_normalized != optimized_normalized:
            raise AssertionError("Optimized results do not match baseline results.")

        speedup = (
            baseline_seconds / optimized_seconds
            if optimized_seconds > 0 else float("inf")
        )
        per_read_saving = baseline_seconds - optimized_seconds
        break_even_reads = (
            int(refresh_seconds / per_read_saving) + 1
            if per_read_saving > 0 else 0
        )
        improvement = (
            (1 - optimized_seconds / baseline_seconds) * 100
            if baseline_seconds > 0 else 0
        )

        report = f"""YottaFlex AI - SQL Performance Benchmark

Workload:
- 100,000 orders joined to 100 products.
- Group sales by product category.
- 25 timed repetitions after one warm-up execution.
- Median query time is reported to reduce timing noise.

Baseline:
- Execute JOIN + GROUP BY against the detailed orders and products tables.
- Median query time: {baseline_seconds:.6f} seconds.

Optimization:
- Refresh a materialized category_sales_summary table once after loading.
- Repeated analytical reads query the five pre-aggregated category rows.
- Summary refresh time: {refresh_seconds:.6f} seconds.
- Median optimized read time: {optimized_seconds:.6f} seconds.

Measured result:
- Read-query speedup: {speedup:.2f}x.
- Read-query time reduction: {improvement:.2f}%.
- Result equivalence: PASS (category totals match to 2 decimal places).
- Approximate repeated reads needed to recover summary refresh cost: {break_even_reads}.

Trade-off:
- The summary must be refreshed after source orders or product prices change.
- The refresh has an upfront cost; this optimization is most useful when the
  same category-level report is queried repeatedly.
- Timings depend on the machine, SQLite version, and cache state.
"""
        (report_dir / "performance_report.txt").write_text(report, encoding="utf-8")
        print(report)
    finally:
        connection.close()


if __name__ == "__main__":
    run_benchmark()
