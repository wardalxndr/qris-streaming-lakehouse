{{ config(materialized='view') }}

-- Staging: parse string jadi tipe bener. ts CSV "%Y-%m-%d %H:%M"
-- tidak valid buat TIMESTAMP BigQuery, jadi parse di sini.
select
  txn_id,
  user_id,
  merchant_id,
  merchant_cat,
  city,
  device_id,
  channel,
  cast(amount as int64) as amount,
  parse_timestamp('%Y-%m-%d %H:%M', ts) as event_ts,
  date(parse_timestamp('%Y-%m-%d %H:%M', ts)) as event_date,
  is_fraud = '1' as is_fraud_flag,
  fraud_type
from {{ source('qris', 'silver_transactions') }}
