# Use Cases - siapa pakai apa

| ID | Aktor | Kebutuhan | Output sistem | Bukti |
|---|---|---|---|---|
| UC-01 | Analis fraud | Tiap pagi tau merchant mana dicek duluan | Dashboard tile volume + fraud per tipe | Looker 3 tile |
| UC-02 | Analis fraud | Tau user mana yang bahaya | Skor risiko 0-10 + band high/medium/low | `mart_user_risk` |
| UC-03 | Data engineer | Pipeline jalan ulang identik kapan pun | Generator seed 42 + run 1 perintah | `run_pipeline.py` |
| UC-04 | Data engineer | Tahu kalau data busuk masuk | Quality report per lapis + run gagal keras | `reports/quality_report.json` |
| UC-05 | Stakeholder | Keputusan berbasis angka, bukan feeling | Memo + mart teruji (dbt 17/17) | Dashboard + `dbt test` |
| UC-06 | ML engineer | Model tidak busuk diam-diam | Reconcile metrik + retrain gate (seri = tidak naik) | `reports/reconcile_metrics.json` |

Satu baris satu janji yang bisa dicek. Tidak ada use case tanpa bukti.
