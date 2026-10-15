
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select city
from `epoch-ai-data-center`.`qris_analytics`.`mart_merchant_volume`
where city is null



  
  
      
    ) dbt_internal_test