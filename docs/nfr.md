# NFR - Kebutuhan Non Fungsional

Fungsi menjawab "sistem bisa apa". NFR menjawab "sistem harus sebagus apa". Semua target di bawah bisa dites, bukan sekadar harapan.

## 1. Tabel NFR

| ID | Kategori | Kebutuhan | Target terukur | Bukti |
|---|---|---|---|---|
| NFR-01 | Reproducibility | Ulangi kapan pun hasil sama | Generator seed 42, 100.000 baris identik tiap run | `python pipeline/run_pipeline.py` dua kali, diff `quality_report.json` kosong |
| NFR-02 | Reliability stream | Tidak hilang saat consumer mati | Produce 100K, consumer mati di tengah, catch up 100.000/100.000, 0 duplikat, 0 hilang | `logs/` + `data/qris_clean_live.csv` count 100.000 |
| NFR-03 | Data quality | Baris busuk tidak lolos diam diam | 0 duplikat di silver, semua reject tercatat di quality report | `reports/quality_report.json`: total 100.000, high_risk_users 39 |
| NFR-04 | Performance batch | Run harian selesai di laptop | Full run generate ke forecast < 10 menit di laptop 8GB, tanpa cluster | Waktu run tercatat di `logs/` |
| NFR-05 | Performance query | Dashboard tidak lemot dan murah | Mart BigQuery partitioned by day, query 7 hari scan < 1 GB | Partisi `event_date` di `qris_analytics`, cek di console BigQuery |
| NFR-06 | Observability | Tiap lapis bisa diaudit | Bronze count, silver reject reason, gold mart count, model metric semua ada file | `reports/quality_report.json`, `reports/model_metrics.json`, `reports/reconcile_metrics.json` |
| NFR-07 | Maintainability model | Model tidak busuk diam diam | Reconcile jalan tiap retrain, challenger naik cuma kalau F1 menang >= 0.005, model lama tidak dihapus | `reports/model_registry.json` + `reports/retrain_report.json` (kemarin seri jadi tidak naik) |
| NFR-08 | Security | Kredensial tidak bocor, akses minimal | Service account JSON tidak di commit, load pakai env var, dashboard read only ke marts bukan ke silver | `.gitignore` berisi `*service-account*.json`, code `load_to_bq.py` baca dari env |
| NFR-09 | Usability | Analis paham tanpa baca code | Dashboard 3 tile bahasa bisnis: merchant bocor, tren fraud harian, user high risk | Link Looker di README, 3 tile sesuai `docs/flows.md` |
| NFR-10 | Scalability | Naik 10x tanpa ubah logika | Pattern sama untuk 1 juta baris, tinggal tambah partisi Kafka dan partisi BQ, Spark reference sudah ada | `spark/` sebagai referensi Structured Streaming, `docker-compose.kafka.yml` 3 partisi |

## 2. Batas jujur (biar tidak overclaim pas interview)

1. Security NFR-08 baru di level kredensial dan akses baca. Belum ada masking PII, belum ada audit login per user. Kalau jadi production, tambah IAM per peran + mask `user_id` untuk stakeholder.
2. Late label belum backfill otomatis ke mart. `reconcile.py` lapor metrik dengan delay 2 hari, tapi mart tidak dihitung ulang otomatis. Ini ditulis eksplisit di `docs/edge-cases.md`.
3. Out of order stream belum pakai watermark. Velocity window dihitung dari timestamp event per bucket 10 menit, cukup untuk 100K ini tapi belum siap untuk event telat jauh.

## 3. Cara pakai pas interview user

Kalau user tanya "NFR nya apa", jangan hafal tabel. Jawab 3 saja: tidak hilang (NFR-02), bisa diulang identik (NFR-01), bisa diaudit tiap lapis (NFR-06). Sisanya buat jawaban susulan kalau ditanya soal cost, security, scalability.
