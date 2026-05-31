# Appendix Evidence

## Ringkasan Sampel

- Jumlah sampled review: 24,964
- Jumlah produk unik: 19,425
- Sumber utama dataset: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Dokumentasi field dataset: https://amazon-reviews-2023.github.io/main.html

## Bukti KPI

File tabel:

- `outputs/tables/kpi_table.csv`
- `outputs/tables/monthly_rating.csv`
- `outputs/tables/sample_summary.csv`

Grafik:

- `outputs/figures/rating_distribution.png`
- `outputs/figures/monthly_avg_rating.png`

## Bukti Voice of Customer

File tabel:

- `outputs/tables/voc_themes.csv`
- `outputs/tables/review_segment_comparison.csv`
- `outputs/tables/business_translation.csv`

Grafik:

- `outputs/figures/complaint_themes.png`

## Bukti Model Prediktif

Model: Logistic Regression  
Fitur: review text (`TF-IDF`), review length, helpful votes

File evaluasi:

- `outputs/tables/model_metrics.csv`
- `outputs/tables/classification_report.csv`
- `outputs/figures/confusion_matrix.png`

## Catatan Metodologi

1. Dataset kategori asli `Beauty_and_Personal_Care` berukuran sangat besar, sehingga analisis dikerjakan pada streaming sample yang diambil langsung dari file resmi dataset.
2. Preprocessing meliputi pembersihan teks, penggabungan judul dan isi review, perhitungan panjang review, serta pembentukan label review baik vs buruk.
3. Tema keluhan diidentifikasi dengan pendekatan keyword-based thematic coding agar hasil mudah dijelaskan ke konteks bisnis.
