# Spesifikasi Fraud — 4 tipologi + metrik

## Tipologi (bahasa bisnis)

| Tipe | Artinya | Bobot risiko |
|---|---|---|
| velocity | 1 user >= 5 transaksi per 10 menit | 4 |
| velocity_detected | Sama, ketahuan oleh gate (bukan label awal) | 4 |
| night | Transaksi jam rawan | 3 |
| round_amount | Nominal bulat (pola testing kartu) | 2 |
| new_device | Device baru belum dikenal | 2 |

Skor user = jumlah bobot, dibatasi 10. Band: high >= 8, medium >= 4, low.

## Metrik model (jujur, di file)

- Classifier: LogisticRegression, fitur nominal + jam + kategori + kota + gajian.
- Split waktu: latih 3 minggu, uji 1 minggu ke depan.
- Threshold dipilih pakai F1, bukan asal 0.5.
- Retrain gate: challenger naik cuma kalau F1 menang >= 0.005.
  Kemarin seri, jadi tidak naik. Buktinya di `reports/retrain_report.json`.
- Angka persisnya: `reports/model_metrics.json`.

## Kenapa ini penting buat risk & finance

Fraud kecil yang lolos tiap hari = bocor diam-diam. Sistem ini bikin
bocornya kelihatan (dashboard), terukur (skor), dan modelnya diawasi
(reconcile). Risk dapat prioritas harian, finance dapat angka buat
keputusan. Itu business requirement-nya, bukan sekadar akurasi model.
