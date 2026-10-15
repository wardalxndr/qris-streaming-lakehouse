{{ config(
    materialized='table',
    cluster_by=['user_id']
) }}

-- Skor risiko per user. TIDAK di-partition sengaja: ini snapshot
-- per user (bukan series waktu), partition tidak menghemat apa pun.
-- Cluster user_id karena semua lookup filter user.
with scored as (
  select
    user_id,
    case fraud_type
      when 'velocity' then 4
      when 'velocity_detected' then 4
      when 'night' then 3
      when 'round_amount' then 2
      when 'new_device' then 2
      else 1
    end as w
  from {{ ref('stg_qris') }}
  where is_fraud_flag
),
agg as (
  select user_id, sum(w) as risk_score
  from scored
  group by 1
)
select
  user_id,
  least(risk_score, 10) as risk_score,
  case
    when risk_score >= 8 then 'high'
    when risk_score >= 4 then 'medium'
    else 'low'
  end as risk_band
from agg
