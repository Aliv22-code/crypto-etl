"""
Day 4 — Load crypto price records into Postgres.
"""
import os
import logging
import psycopg2
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "crypto_db"),
        user=os.getenv("DB_USER", "crypto_user"),
        password=os.getenv("DB_PASSWORD", "crypto_pass"),
    )


def load_prices(records: list[dict]) -> int:
    """Insert price records into crypto_prices. Returns inserted count."""
    if not records:
        log.warning("No records to load.")
        return 0

    sql = """
        INSERT INTO crypto_prices
            (coin_id, price_usd, market_cap_usd,
             volume_24h_usd, price_change_24h_pct, fetched_at)
        VALUES
            (%(coin_id)s, %(price_usd)s, %(market_cap_usd)s,
             %(volume_24h_usd)s, %(price_change_24h_pct)s, %(fetched_at)s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, records)
        conn.commit()
        log.info("Inserted %d records into crypto_prices", len(records))
        return len(records)
    finally:
        conn.close()