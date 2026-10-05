-- 1. Merchant dengan fraud amount tertinggi
SELECT merchant_id, merchant_cat, city,
       SUM(total_amount) AS vol, SUM(txn_count) AS n
FROM mart_merchant_volume GROUP BY 1, 2, 3 ORDER BY vol DESC LIMIT 10;

-- 2. Jam tersibuk vs jam maling (butuh silver)
-- SELECT SUBSTR(ts, 12, 2) AS jam, COUNT(*) FROM qris_clean GROUP BY 1 ORDER BY 1;

-- 3. Distribusi risk band
SELECT risk_band, COUNT(*) AS users FROM mart_user_risk GROUP BY 1;
