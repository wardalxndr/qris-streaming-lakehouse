
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select user_id
from `epoch-ai-data-center`.`qris_analytics`.`mart_user_risk`
where user_id is null



  
  
      
    ) dbt_internal_test