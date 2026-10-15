
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select count
from `epoch-ai-data-center`.`qris_analytics`.`mart_fraud_flags`
where count is null



  
  
      
    ) dbt_internal_test