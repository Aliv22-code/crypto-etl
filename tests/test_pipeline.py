"""
Unit test for pipeline.py — mocks extract, validate and load
so no real API call or DB connection is needed.
"""
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from pipelines.pipeline import run

MOCK_RECORDS = [
    {
        "coin_id":              "bitcoin",
        "price_usd":            67000.0,
        "market_cap_usd":       1.3e12,
        "volume_24h_usd":       28e9,
        "price_change_24h_pct": 2.5,
        "fetched_at":           datetime.now(timezone.utc),
    }
]


@patch("pipelines.pipeline.load_prices",    return_value=1)
@patch("pipelines.pipeline.validate_records", return_value=MOCK_RECORDS)
@patch("pipelines.pipeline.fetch_prices",   return_value=MOCK_RECORDS)
def test_pipeline_run_returns_inserted_count(mock_fetch, mock_validate, mock_load):
    result = run()
    assert result == 1


@patch("pipelines.pipeline.load_prices",    return_value=1)
@patch("pipelines.pipeline.validate_records", return_value=MOCK_RECORDS)
@patch("pipelines.pipeline.fetch_prices",   return_value=MOCK_RECORDS)
def test_pipeline_calls_each_step_once(mock_fetch, mock_validate, mock_load):
    run()
    mock_fetch.assert_called_once()
    mock_validate.assert_called_once()
    mock_load.assert_called_once()