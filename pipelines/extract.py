"""
Day 2 — Extract crypto prices from CoinGecko free API.
No API key needed. Run this file directly to test it.
"""
import requests
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Coins we want to track
COINS = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]

# CoinGecko free endpoint — no key required
API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices(coins: list[str] = COINS) -> list[dict]:
    """
    Call CoinGecko and return a list of price records.
    Each record looks like:
      {
        "coin_id": "bitcoin",
        "price_usd": 67432.0,
        "market_cap_usd": 1324000000000.0,
        "volume_24h_usd": 28000000000.0,
        "price_change_24h_pct": 2.34,
        "fetched_at": datetime(...)
      }
    """
    log.info("Fetching prices for: %s", coins)

    response = requests.get(
        API_URL,
        params={
            "ids": ",".join(coins),
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        },
        timeout=10,
    )
    response.raise_for_status()   # raises on 4xx / 5xx
    data = response.json()

    fetched_at = datetime.now(timezone.utc)

    records = []
    for coin in coins:
        if coin not in data:
            log.warning("No data returned for coin: %s", coin)
            continue

        info = data[coin]
        records.append({
            "coin_id":             coin,
            "price_usd":           info.get("usd"),
            "market_cap_usd":      info.get("usd_market_cap"),
            "volume_24h_usd":      info.get("usd_24h_vol"),
            "price_change_24h_pct": info.get("usd_24h_change"),
            "fetched_at":          fetched_at,
        })

    log.info("Fetched %d coin records", len(records))
    return records


# ── Run this file directly to test the API call ───────────────────────────────
if __name__ == "__main__":
    prices = fetch_prices()
    for p in prices:
        print(f"{p['coin_id']:12s}  ${p['price_usd']:>12,.2f}  "
              f"24h change: {p['price_change_24h_pct']:+.2f}%")