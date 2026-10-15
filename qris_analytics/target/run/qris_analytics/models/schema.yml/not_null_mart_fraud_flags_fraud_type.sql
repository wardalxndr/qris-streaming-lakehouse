
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select fraud_type
from `epoch-ai-data-center`.`qris_analytics`.`mart_fraud_flags`
where fraud_type is null



  
  
      
    ) dbt_internal_test