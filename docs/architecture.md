# Arsitektur & DFD - QRIS Lakehouse

## Diagram konteks (level 0)

```mermaid
flowchart LR
    GEN["Generator QRIS\n(seed 42)"] -->|100K event| SYS["QRIS Lakehouse"]
    KAFKA["Kafka cluster"] --> SYS
    SYS -->|dashboard 3 tile| ANALIS["Analis Fraud"]
    SYS -->|marts + metrik| STAKE["Stakeholder"]
    SYS -->|quality report| ENG["Data Engineer"]
```

Satu sistem, tiga konsumen. Analis dapat jawaban, stakeholder dapat
keputusan, engineer dapat alarm kalau ada yang busuk.

## DFD level 1 (aliran data)

```mermaid
flowchart LR
    P["produce.py\n100K event"] --> BR["bronze/qris_raw.csv\nmentah"]
    BR --> C["clean_silver.py\ndedup + validasi +\nflag velocity"]
    C --> S["qris_clean.csv\nsilver"]
    C --> QR["quality_report.json"]
    S --> G["build_gold.py\n3 mart"]
    S --> LQ["load_to_bq.py\nBigQuery"]
    G --> LQ
    LQ --> DBT["dbt 4 model\n+ 17 test"]
    DBT --> BQ["marts Partitioned\nBigQuery"]
    BQ --> LK["Looker 3 tile"]
    S --> ML["model.py\nclassifier"]
    ML --> MM["model_metrics.json"]
    MM --> RT["reconcile + retrain\n+ forecast"]
```

Aturan baca: kotak = proses/file, panah = data mengalir. Tidak ada
panah dua arah: data tidak pernah jalan mundur.

Dashboard live (Looker Studio, 3 tile): [QRIS Fraud Analytics](https://datastudio.google.com/reporting/a1e01ca3-4d6d-466e-b8d4-f32954e4b872/page/PvWAG).
