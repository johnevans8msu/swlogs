with hits_cte as (
    select 
        useragent as ua,
        count(*) as hits
    from staging
    group by 1
    order by hits desc 
    limit 20
),
error_count_cte as (
    select 
        useragent as ua,
        count(*) as errors
    from staging
    where status > 399
    group by 1
),
c429_cte as (
    select 
        useragent as ua,
        count(*) as hits
    from staging
    where status = 429
    group by 1
),
robots_cte as (
    select 
        useragent as ua,
        count(*) as hits
    from staging
    where url ~ '/robots.txt'
    group by 1
),
xmlui_cte as (
    select 
        useragent as ua,
        count(*) as hits
    from staging
    where url ~ '/xmlui'
    group by 1
),
sitemaps_cte as (
    select 
        useragent as ua,
        count(*) as hits
    from staging
    where url ~ '/sitemap'
    group by 1
),
item_pct_cte as (
    select 
        useragent as ua,
        count(*) as hits
    from staging
    where url ~ '^/items/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$'
    group by 1
)
insert into bots
(ua, hits, error_pct, c429, robots, xmlui, sitemaps, item_pct, date)
select
    hits_cte.ua as ua,
    hits_cte.hits,
    case
	when error_count_cte.errors is null then 0
        else error_count_cte.errors::real / hits_cte.hits::real * 100
    end as error_pct,
    case
	when c429_cte.hits is null then 0
        else c429_cte.hits
    end as c429,
    case
	when robots_cte.hits is null then false
        else true
    end as robots,
    case
	when xmlui_cte.hits is null then false
        else true
    end as xmlui,
    case
	when sitemaps_cte.hits is null then false
        else true
    end as sitemaps,
    case
	when item_pct_cte.hits is null then 0
        else item_pct_cte.hits::real / hits_cte.hits::real * 100
    end as item_pct,
    current_date - 1 as date
from hits_cte
    left join error_count_cte using(ua)
    left join c429_cte using(ua)
    left join robots_cte using(ua)
    left join xmlui_cte using(ua)
    left join sitemaps_cte using(ua)
    left join item_pct_cte using(ua)
order by hits desc
;
