{{ config(
    materialized='table',
    partition_by={'field': 'day', 'data_type': 'date'},
    cluster_by=['fraud_type']
) }}

-- Fraud per tipe per hari. Partition day (filter tanggal),
-- cluster fraud_type (tile selalu breakdown per tipe).
select
  event_date as day,
  fraud_type,
  count(*) as count
from {{ ref('stg_qris') }}
where is_fraud_flag
group by 1, 2
