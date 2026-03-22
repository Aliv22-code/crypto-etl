-- Custom test: fails if any price_usd is zero or negative
-- dbt tests PASS when this query returns 0 rows

select
    id,
    coin_id,
    price_usd
from {{ ref('stg_crypto_prices') }}
where price_usd <= 0