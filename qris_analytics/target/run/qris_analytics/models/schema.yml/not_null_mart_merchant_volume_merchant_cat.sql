
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select merchant_cat
from `epoch-ai-data-center`.`qris_analytics`.`mart_merchant_volume`
where merchant_cat is null



  
  
      
    ) dbt_internal_test