{{ config(
    materialized='table',
    partition_by={'field': 'day', 'data_type': 'date'},
    cluster_by=['merchant_id']
) }}

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
from {{ ref('stg_qris') }}
group by 1, 2, 3, 4
