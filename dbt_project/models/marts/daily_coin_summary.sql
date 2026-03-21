-- Mart: daily price summary per coin

select
    day,
    coin_id,
    round(avg(price_usd)::numeric, 2)            as avg_price_usd,
    round(max(price_usd)::numeric, 2)            as high_price_usd,
    round(min(price_usd)::numeric, 2)            as low_price_usd,
    round(avg(volume_24h_usd)::numeric, 2)       as avg_volume_usd,
    round(avg(price_change_24h_pct)::numeric, 4) as avg_change_pct,
    count(*)                                     as fetch_count

from {{ ref('stg_crypto_prices') }}
group by 1, 2
order by 1 desc, 2