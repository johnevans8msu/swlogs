with hits_cte as (
    select
        ip,
        count(*) as hits
    from staging
    group by ip
    order by 2 desc
    limit 30
),
error_cte as (
    select
        ip,
        count(*) as errors
    from staging
    where status > 399
    group by ip
)
insert into ip32
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

