
  
    

    create or replace table `epoch-ai-data-center`.`qris_analytics`.`mart_merchant_volume`
      
    partition by day
    cluster by merchant_id

    
    OPTIONS()
    as (
      

-- Volume per merchant per hari. Partition day karena semua query
-- dashboard filter rentang tanggal; cluster merchant_id karena
-- tile utama group by merchant.
select
  merchant_id,
  merchant_cat,
  city,
  event_date as day,
  count(*) as txn_count,
  sum(amount) as total_amount
from `epoch-ai-data-center`.`qris_analytics`.`stg_qris`
group by 1, 2, 3, 4
    );
  