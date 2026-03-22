"""
Day 15 — Prefect flow with hourly schedule.
Runs automatically every hour via Prefect Cloud.
"""
import subprocess
from datetime import timedelta
from prefect import flow, task
from prefect.logging import get_run_logger

from pipelines.extract import fetch_prices
from pipelines.load    import load_prices



# ── Tasks ─────────────────────────────────────────────────────────────────────

@task(name="extract-crypto-prices", retries=3, retry_delay_seconds=30)
def extract_task():
    """Fetch prices from CoinGecko. Retries 3 times if API is down."""
    log = get_run_logger()
    records = fetch_prices()
    log.info("Extracted %d records", len(records))
    return records


@task(name="load-to-postgres", retries=2, retry_delay_seconds=20)
def load_task(records: list[dict]):
    """Insert clean records into Postgres."""
    log = get_run_logger()
    count = load_prices(records)
    log.info("Loaded %d records into Postgres", count)
    return count


@task(name="dbt-run")
def dbt_run_task():
    """Build dbt models after new data is loaded."""
    log = get_run_logger()
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", "."],
        cwd="dbt_project",
        capture_output=True,
        text=True
    )
    log.info(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"dbt run failed:\n{result.stderr}")
    log.info("dbt models built successfully")


@task(name="dbt-test")
def dbt_test_task():
    """Run dbt data quality tests."""
    log = get_run_logger()
    result = subprocess.run(
        ["dbt", "test", "--profiles-dir", "."],
        cwd="dbt_project",
        capture_output=True,
        text=True
    )
    log.info(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"dbt test failed:\n{result.stderr}")
    log.info("All dbt tests passed")


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="crypto-etl-pipeline",
    description="Fetch crypto prices → load → dbt transform → dbt test",
    log_prints=True
)
def crypto_pipeline():
    records = extract_task()
    count   = load_task(records)
    dbt_run_task()
    dbt_test_task()
    print(f"Pipeline complete — {count} records loaded and transformed.")
    return count


# ── Deploy with 6-hour schedule ──────────────────────────────────────────────
if __name__ == "__main__":
    crypto_pipeline.serve(
        name="crypto-pipeline-6h",
        interval=timedelta(hours=6),
        pause_on_shutdown=False,
    )