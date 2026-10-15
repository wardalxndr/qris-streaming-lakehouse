
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        risk_band as value_field,
        count(*) as n_records

    from `epoch-ai-data-center`.`qris_analytics`.`mart_user_risk`
    group by risk_band

)

select *
from all_values
where value_field not in (
    'high','medium','low'
)



  
  
      
    ) dbt_internal_test