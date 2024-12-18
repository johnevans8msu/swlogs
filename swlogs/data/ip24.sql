with hits_cte as (
    select
        network(set_masklen(ip, 24)) as ip,
        count(*) as hits
    from swlogs.staging
    group by 1
    order by 2 desc
    limit 30
),
error_cte as (
    select
        network(set_masklen(ip, 24)) as ip,
        count(*) as errors
    from swlogs.staging
    where status > 399
    group by 1
)
insert into swlogs.ip24
(ip, hits, error_pct, date)
select
    hits_cte.ip,
    hits_cte.hits,
    case
        when errors is null then 0
        else error_cte.errors::real / hits_cte.hits::real * 100
    end as error_pct,
    current_date - 1
from hits_cte left join error_cte using(ip)
order by 2 desc
;


