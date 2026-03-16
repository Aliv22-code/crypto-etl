
CREATE TABLE IF NOT EXISTS crypto_prices (
    id                   SERIAL PRIMARY KEY,
    coin_id              TEXT        NOT NULL,
    price_usd            NUMERIC     NOT NULL,
    market_cap_usd       NUMERIC,
    volume_24h_usd       NUMERIC,
    price_change_24h_pct NUMERIC,
    fetched_at           TIMESTAMPTZ NOT NULL
);