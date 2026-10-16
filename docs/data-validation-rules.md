# Aturan Validasi Data — Silver Gate

Gate di `clean_silver.py`. Baris yang gagal tidak masuk silver,
semuanya dihitung dan dilaporkan di `quality_report.json`.

| # | Aturan bisnis | Aksi | Kenapa |
|---|---|---|---|
| R1 | `txn_id` unik | Duplikat dibuang, yang pertama menang | Retry jaringan bikin dobel kirim; tanpa ini mart double count |
| R2 | `amount` integer > 0 | Gagal parse / nol / negatif dibuang | Nominal aneh = data rusak atau test nyasar, merusak agregat |
| R3 | `ts` format `%Y-%m-%d %H:%M` | Gagal parse dibuang | Timestamp rusak bikin window velocity dan partition ngaco |
| R4 | Velocity: 1 user >= 5 transaksi per 10 menit | Flag `velocity_detected`, `is_fraud = 1` | Pola klasik kartu dicuri: gas banyak transaksi cepat |
| R5 | Kolom wajib lengkap 11 field | Baris pincang dibuang | Kontrak payload dilanggar = tolak, bukan tebak |

Prinsip: tolak dengan catatan, jangan tebak diam-diam.
