-- Custom test: fails if any expected coin is missing from top_movers
-- dbt tests PASS when this query returns 0 rows

with expected as (
    select unnest(array[
        'bitcoin', 'ethereum', 'solana', 'cardano', 'dogecoin'
    ]) as coin_id
),
actual as (
    select distinct coin_id
    from {{ ref('top_movers') }}
)
select e.coin_id
from expected e
left join actual a on e.coin_id = a.coin_id
where a.coin_id is null      -- coin expected but not found