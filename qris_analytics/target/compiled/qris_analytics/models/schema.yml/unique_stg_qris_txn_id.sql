
    
    

with dbt_test__target as (

  select txn_id as unique_field
  from `epoch-ai-data-center`.`qris_analytics`.`stg_qris`
  where txn_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


