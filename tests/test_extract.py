"""
Day 6 — Unit tests for extract.py
Uses unittest.mock to fake the API call — no internet needed.
"""
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from pipelines.extract import fetch_prices


# Fake API response that CoinGecko would return
MOCK_API_RESPONSE = {
    "bitcoin":  {"usd": 67000.0, "usd_market_cap": 1.3e12, "usd_24h_vol": 28e9, "usd_24h_change": 2.5},
    "ethereum": {"usd": 3500.0,  "usd_market_cap": 4.2e11, "usd_24h_vol": 15e9, "usd_24h_change": -1.2},
}


@patch("pipelines.extract.requests.get")
def test_fetch_returns_correct_number_of_records(mock_get):
    mock_get.return_value.json.return_value = MOCK_API_RESPONSE
    mock_get.return_value.raise_for_status = MagicMock()

    result = fetch_prices(["bitcoin", "ethereum"])
    assert len(result) == 2


@patch("pipelines.extract.requests.get")
def test_fetch_record_has_required_fields(mock_get):
    mock_get.return_value.json.return_value = MOCK_API_RESPONSE
    mock_get.return_value.raise_for_status = MagicMock()

    result = fetch_prices(["bitcoin"])
    record = result[0]

    assert record["coin_id"]   == "bitcoin"
    assert record["price_usd"] == 67000.0
    assert record["market_cap_usd"]       is not None
    assert record["volume_24h_usd"]       is not None
    assert record["price_change_24h_pct"] is not None
    assert isinstance(record["fetched_at"], datetime)


@patch("pipelines.extract.requests.get")
def test_missing_coin_is_skipped(mock_get):
    """If CoinGecko returns no data for a coin, skip it gracefully."""
    mock_get.return_value.json.return_value = MOCK_API_RESPONSE
    mock_get.return_value.raise_for_status = MagicMock()

    # "solana" is not in MOCK_API_RESPONSE — should be silently skipped
    result = fetch_prices(["bitcoin", "solana"])
    coin_ids = [r["coin_id"] for r in result]

    assert "bitcoin" in coin_ids
    assert "solana"  not in coin_ids


@patch("pipelines.extract.requests.get")
def test_empty_coin_list_returns_empty(mock_get):
    mock_get.return_value.json.return_value = {}
    mock_get.return_value.raise_for_status = MagicMock()

    result = fetch_prices([])
    assert result == []


@patch("pipelines.extract.requests.get")
def test_fetched_at_is_utc(mock_get):
    mock_get.return_value.json.return_value = MOCK_API_RESPONSE
    mock_get.return_value.raise_for_status = MagicMock()

    result = fetch_prices(["bitcoin"])
    assert result[0]["fetched_at"].tzinfo == timezone.utc