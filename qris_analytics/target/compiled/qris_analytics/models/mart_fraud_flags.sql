

-- Fraud per tipe per hari. Partition day (filter tanggal),
-- cluster fraud_type (tile selalu breakdown per tipe).
select
  event_date as day,
  fraud_type,
  count(*) as count
from `epoch-ai-data-center`.`qris_analytics`.`stg_qris`
where is_fraud_flag
group by 1, 2