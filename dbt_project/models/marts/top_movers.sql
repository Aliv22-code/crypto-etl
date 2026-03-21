-- Mart: latest snapshot per coin with movement label

with latest as (
    select
        coin_id,
        max(fetched_at) as latest_fetch
    from {{ ref('stg_crypto_prices') }}
    group by coin_id
)
select
    s.coin_id,
    s.price_usd,
    s.market_cap_usd,
    s.volume_24h_usd,
    s.price_change_24h_pct,
    s.fetched_at,
    case
        when s.price_change_24h_pct >  2 then 'gainer'
        when s.price_change_24h_pct < -2 then 'loser'
        else 'stable'
    end as movement_label

from {{ ref('stg_crypto_prices') }} s
inner join latest l
    on  s.coin_id     = l.coin_id
    and s.fetched_at  = l.latest_fetch
order by s.price_change_24h_pct desc