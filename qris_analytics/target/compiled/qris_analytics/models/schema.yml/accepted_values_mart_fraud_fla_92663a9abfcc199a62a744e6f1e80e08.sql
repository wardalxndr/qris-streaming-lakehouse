
    
    

with all_values as (

    select
        fraud_type as value_field,
        count(*) as n_records

    from `epoch-ai-data-center`.`qris_analytics`.`mart_fraud_flags`
    group by fraud_type

)

select *
from all_values
where value_field not in (
    'velocity','velocity_detected','night','round_amount','new_device'
)


