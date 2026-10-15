
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select risk_score
from `epoch-ai-data-center`.`qris_analytics`.`mart_user_risk`
where risk_score is null



  
  
      
    ) dbt_internal_test