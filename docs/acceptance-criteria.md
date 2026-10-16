# Acceptance Criteria - Kapan dibilang selesai

Satu use case dianggap selesai kalau semua checklist di bawah lolos. Format Given When Then biar tester dan user bisa ulang tanpa tanya pembuatnya.

Traceability: UC-01 sampai UC-06 sama persis dengan `docs/use-cases.md`.

## UC-01: Analis tau merchant mana dicek duluan

**Given** pipeline sudah run penuh dan BigQuery `qris_analytics` sudah di load
**When** analis buka dashboard tile merchant volume pagi hari
**Then** tile tampil: top merchant by fraud volume + total amount hari ini

Cek:
1. `SELECT COUNT(*) FROM qris_analytics.mart_merchant_volume` > 0 dan tidak double count vs silver
2. `SELECT SUM(txn_count) FROM mart_merchant_volume` = 100.000 setelah dedup
3. Dashboard 3 tile bisa dibuka dari link README tanpa error

Lolos kalau: angka 1 dan 2 sama dengan `reports/quality_report.json` total 100.000.

## UC-02: Analis tau user mana yang bahaya

**Given** gold sudah dibuild
**When** analis filter risk_band = high
**Then** muncul list user skor >= 8 beserta bobot penyebabnya

Cek:
1. `SELECT COUNT(*) FROM mart_user_risk WHERE risk_band = 'high'` = 39
2. Semua skor antara 0 sampai 10, tidak ada null
3. Rumus skor = velocity 4 + night 3 + round_amount 2 + new_device 2 sesuai `docs/fraud-specifications.md`

Lolos kalau: jumlah high = 39 sama dengan quality report.

## UC-03: Engineer bisa rerun identik

**Given** laptop fresh clone repo
**When** engineer jalan `python pipeline/run_pipeline.py`
**Then** hasil sama persis dengan run sebelumnya tanpa edit manual

Cek:
1. Run dua kali, `diff reports/quality_report.json` kosong
2. Seed 42 tercatat di `pipeline/gen_qris.py`
3. Satu perintah saja, tidak ada step manual tersembunyi

Lolos kalau: total tetap 100.000 dan fraud rate sekitar 1.95 persen.

## UC-04: Data busuk ketahuan bukan lolos diam diam

**Given** bronze berisi duplikat dan baris rusak simulasi retry
**When** `clean_silver.py` jalan
**Then** duplikat dibuang yang pertama menang, baris rusak dibuang plus dicatat alasannya

Cek:
1. `SELECT COUNT(DISTINCT txn_id) = COUNT(*)` di silver, artinya 0 duplikat
2. `reports/quality_report.json` ada dan terbaca
3. Run gagal keras kalau kontrak payload dilanggar, tidak lanjut ke gold

Lolos kalau: cek 1 benar dan quality report konsisten.

## UC-05: Stakeholder dapat angka buat keputusan

**Given** dbt models sudah jalan
**When** stakeholder minta bukti angka valid
**Then** engineer tunjukkan `dbt test` lolos semua dan dashboard sama dengan mart

Cek:
1. `dbt test` 17/17 passed
2. Angka dashboard tile fraud harian = `SELECT day, count FROM mart_fraud_flags ORDER BY day`
3. Memo keputusan nyebut sumber mart bukan feeling

Lolos kalau: dbt 17/17 dan tidak ada selisih dashboard vs query langsung.

## UC-06: Model tidak busuk diam diam

**Given** champion model sudah ada di registry
**When** `run_retrain.py` jalan (score ke reconcile ke retrain)
**Then** reconcile lapor precision recall F1 dengan delay 2 hari, challenger cuma naik kalau menang >= 0.005

Cek:
1. `reports/reconcile_metrics.json` ada: precision 0.34, recall 0.257, F1 0.293, labeled 95009, unlabeled 4991
2. `reports/model_metrics.json` ada: threshold 0.1, precision 0.356, recall 0.236, F1 0.284
3. `reports/retrain_report.json` bilang seri jadi tidak naik, model lama tetap ada di `model_registry.json`

Lolos kalau: monitoring selalu exit 0 dan tidak ada model yang dihapus.

## Cara pakai pas interview

Bawa satu contoh saja, UC-01 atau UC-02, lalu bilang: ini Given nya, ini Then nya, ini query buktinya. User langsung percaya karena bisa dites, bukan klaim.
