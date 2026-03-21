-- Staging: clean view on top of raw crypto_prices
-- Adds derived date/time columns for downstream models

select
    id,
    coin_id,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_24h_pct,
    fetched_at,

    fetched_at::date                        as fetched_date,
    date_part('hour', fetched_at)::int      as fetched_hour,
    date_trunc('day',  fetched_at)          as day,
    date_trunc('hour', fetched_at)          as hour

from {{ source('public', 'crypto_prices') }}
