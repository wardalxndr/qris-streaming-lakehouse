# Skema Data & ERD - QRIS Lakehouse

## Silver (fakta mentah bersih): `silver_transactions`

Satu baris = satu transaksi unik (dedup by `txn_id`).

```mermaid
erDiagram
    SILVER_TRANSACTIONS {
        string txn_id PK
        string ts
        string user_id FK
        string merchant_id FK
        string merchant_cat
        int amount
        string city
        string device_id
        string channel
        string is_fraud
        string fraud_type
    }
    DIM_MERCHANT {
        string merchant_id PK
        string merchant_cat
        string city
    }
    DIM_USER {
        string user_id PK
    }
    MART_MERCHANT_VOLUME {
        string merchant_id FK
        string merchant_cat
        string city
        date day
        int txn_count
        int total_amount
    }
    MART_FRAUD_FLAGS {
        date day
        string fraud_type
        int count
    }
    MART_USER_RISK {
        string user_id FK
        int risk_score
        string risk_band
    }
    SILVER_TRANSACTIONS ||--o{ MART_MERCHANT_VOLUME : "agregat per merchant/hari"
    SILVER_TRANSACTIONS ||--o{ MART_FRAUD_FLAGS : "agregat fraud/hari"
    SILVER_TRANSACTIONS ||--o{ MART_USER_RISK : "skor per user"
    DIM_MERCHANT ||--o{ MART_MERCHANT_VOLUME : "atribut merchant"
    DIM_USER ||--o{ MART_USER_RISK : "atribut user"
```

## Catatan desain (dibaca reviewer)

- `ts` disimpan STRING di silver karena format sumber `%Y-%m-%d %H:%M`
  bukan TIMESTAMP valid. Parsing ke TIMESTAMP + DATE (`event_ts`,
  `event_date`) terjadi di dbt staging (`stg_qris`), bukan saat load.
  Keputusan sadar: load tidak pernah gagal gara-gara format tanggal.
- Kolom `day` di mart bertipe DATE (hasil cast), namanya dipertahankan
  supaya dashboard lama tidak perlu ganti field.
- `mart_user_risk` tanpa partition: snapshot per user, bukan series waktu.
  Cluster `user_id` karena semua lookup filter user.
