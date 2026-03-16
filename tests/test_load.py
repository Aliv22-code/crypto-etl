"""
Day 7 — Integration tests for load.py
Requires Docker Postgres running locally (docker-compose up -d)
Skipped automatically if DB is unreachable.
"""
import pytest
from datetime import datetime, timezone
from pipelines.load import get_connection, load_prices


# ── helpers ───────────────────────────────────────────────────────────────────

def db_available() -> bool:
    try:
        get_connection().close()
        return True
    except Exception:
        return False


skip_if_no_db = pytest.mark.skipif(
    not db_available(),
    reason="Postgres not reachable — skipping integration tests"
)

SAMPLE_RECORDS = [
    {
        "coin_id":             "bitcoin",
        "price_usd":           67000.0,
        "market_cap_usd":      1.3e12,
        "volume_24h_usd":      28e9,
        "price_change_24h_pct": 2.5,
        "fetched_at":          datetime.now(timezone.utc),
    },
    {
        "coin_id":             "ethereum",
        "price_usd":           3500.0,
        "market_cap_usd":      4.2e11,
        "volume_24h_usd":      15e9,
        "price_change_24h_pct": -1.2,
        "fetched_at":          datetime.now(timezone.utc),
    },
]


@pytest.fixture
def clean_db():
    """Wipe crypto_prices before each test so tests don't affect each other."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE crypto_prices RESTART IDENTITY;")
    conn.commit()
    conn.close()


# ── tests ─────────────────────────────────────────────────────────────────────

@skip_if_no_db
def test_load_inserts_correct_row_count(clean_db):
    count = load_prices(SAMPLE_RECORDS)
    assert count == 2


@skip_if_no_db
def test_load_data_is_queryable(clean_db):
    load_prices(SAMPLE_RECORDS)

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT coin_id, price_usd FROM crypto_prices ORDER BY coin_id;")
        rows = cur.fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0] == ("bitcoin",  67000.0)
    assert rows[1] == ("ethereum",  3500.0)


@skip_if_no_db
def test_load_empty_list_returns_zero(clean_db):
    count = load_prices([])
    assert count == 0


@skip_if_no_db
def test_multiple_runs_accumulate_rows(clean_db):
    """Running the pipeline twice should store both batches — full history."""
    load_prices(SAMPLE_RECORDS)
    load_prices(SAMPLE_RECORDS)

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM crypto_prices;")
        total = cur.fetchone()[0]
    conn.close()

    assert total == 4   # 2 records × 2 runs