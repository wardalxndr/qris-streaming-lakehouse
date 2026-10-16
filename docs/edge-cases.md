# Edge Cases & NFR - QRIS Lakehouse

Dokumen ini jujur: apa yang ditangani, apa yang belum.

## 1. Idempotency (transaksi ganda karena retry) - DITANGANI

Producer yang retry mengirim `txn_id` yang sama dua kali. Silver menyimpan
set `txn_id` yang sudah lewat dan membuang duplikat (`clean_silver.py`).
Terbukti: consumer dimatikan saat produce 100K event, catch up 100.000 /
100.000, 0 duplikat, 0 hilang.

## 2. Late-arriving data (label telat) - DITANGANI SEBAGIAN

Di produksi label fraud datang belakangan. `reconcile.py` memutar ulang
label dengan delay default 2 hari, melaporkan precision/recall/F1 + flag
drift ke `reports/reconcile_metrics.json`, selalu exit 0 (monitoring,
bukan gate). Yang belum: backfill otomatis ke mart kalau label berubah
setelah agregat dihitung.

## 3. Out-of-order events di stream - BELUM DITANGANI

Consumer memproses sesuai urutan datang, tanpa watermark. Untuk volume
dan pola data sekarang ini cukup (velocity window dihitung per bucket
10 menit dari timestamp event, bukan waktu datang). Kalau jadi production:
tambah watermark + allowed lateness di engine streaming (misal Spark
Structured Streaming yang sudah ada sebagai referensi di `spark/`).

## 4. Skema berubah (kolom baru / tipe berubah) - TERBATAS

Load silver pakai skema eksplisit (kolom tak dikenal ditolak) dan dbt
staging melempar error yang jelas kalau parse gagal. Belum ada schema
registry / evolusi otomatis.

## NFR ringkas

- Reproducibility: generator seed 42, hasil identik tiap run.
- Observability: quality report tiap lapis (duplikat, amount aneh,
  timestamp rusak, velocity flags).
- Cost: 100K event jalan di laptop (Kafka lokal Docker); BigQuery
  partitioned by day supaya query tanggal murah.
