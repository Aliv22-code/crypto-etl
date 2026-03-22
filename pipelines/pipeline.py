"""
Day 5 — Full pipeline: fetch from CoinGecko → save to Postgres.
Run this file to execute the complete pipeline.
"""
import logging
from pipelines.extract import fetch_prices
from pipelines.load import load_prices

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def run():
    log.info("--- Pipeline started ---")

    # Step 1: Extract
    records = fetch_prices()
    log.info("Extracted %d records", len(records))

    # Step 2: Load (no transform needed yet — data is already clean)
    inserted = load_prices(records)
    log.info("Loaded %d records", inserted)

    log.info("--- Pipeline complete ---")
    return inserted


if __name__ == "__main__":
    run()