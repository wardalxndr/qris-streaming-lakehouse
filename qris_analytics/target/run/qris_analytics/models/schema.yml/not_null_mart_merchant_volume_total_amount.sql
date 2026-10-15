
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_amount
from `epoch-ai-data-center`.`qris_analytics`.`mart_merchant_volume`
where total_amount is null



  
  
      
    ) dbt_internal_test