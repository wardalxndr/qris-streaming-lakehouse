# QRIS Event Payload Contract

Kontrak integrasi antara source system (simulator / kasir) dan ingestion layer.
Satu event = satu baris CSV di `data/bronze/qris_raw.csv`, satu message di topik Kafka `qris-txns`.

## Format

CSV, header wajib, encoding UTF-8. Contoh 1 baris:

```csv
txn_id,ts,user_id,merchant_id,merchant_cat,amount,city,device_id,channel,is_fraud,fraud_type
TX-000001,2026-01-05 08:12,U-00042,M-00117,fnb,85000,Jakarta,D-00991,qris,0,-
```

## Field spec

| Field | Tipe | Contoh | Aturan |
|---|---|---|---|
| txn_id | string, unik | TX-000001 | Primary key bisnis. Duplikat dibuang di silver. |
| ts | string `YYYY-MM-DD HH:MM` | 2026-01-05 08:12 | Bukan RFC3339. Di-parse di staging, bukan di-load. |
| user_id | string | U-00042 | Pemilik transaksi. |
| merchant_id | string | M-00117 | Merchant penerima. |
| merchant_cat | string | fnb | Kategori usaha. |
| amount | integer > 0 | 85000 | Rupiah. Nol/negatif/gagal parse = baris dibuang, dicatat. |
| city | string | Jakarta | Kota transaksi. |
| device_id | string | D-00991 | Device pemindai. Dipakai deteksi new_device. |
| channel | string | qris | Kanal pembayaran. |
| is_fraud | "1" / "0" | 0 | Label. String, bukan boolean. |
| fraud_type | string | - | Salah satu: `-` (bersih), `velocity`, `velocity_detected`, `night`, `round_amount`, `new_device`. |

## Versi

v1 (2026-01). Perubahan field = versi baru + catat di sini. Konsumen tidak
boleh asumsi field di luar tabel ini.
