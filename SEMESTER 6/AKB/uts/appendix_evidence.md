# Appendix Evidence

## Ringkasan Data

- Data sumber: file `Beauty_and_Personal_Care.jsonl`
- Total review yang dibaca dari file: 23,911,390
- Data yang dianalisis: 25% sampel dengan metode *proportionate stratified deterministic sampling*
- Total review sampel terproses: 5,976,417
- Sumber dataset: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Dokumentasi field dataset: https://amazon-reviews-2023.github.io/main.html

## Bukti KPI

File tabel:

- `outputs/tables/kpi_table.csv`
- `outputs/tables/monthly_rating.csv`
- `outputs/tables/full_data_summary.csv`

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

Model: Multinomial Naive Bayes  
Fitur utama: teks review yang diubah menjadi fitur hashing bag-of-words

File evaluasi:

- `outputs/tables/model_metrics.csv`
- `outputs/tables/classification_report.csv`
- `outputs/figures/confusion_matrix.png`

## Catatan Metodologi

1. Populasi data berasal dari seluruh file kategori `Beauty_and_Personal_Care.jsonl` dengan total 23.911.390 review.
2. Dari populasi tersebut diambil 25% sampel menggunakan *proportionate stratified deterministic sampling* berdasarkan bulan review dan rating.
3. Proses dilakukan secara streaming agar file besar tetap dapat dianalisis secara efisien dan replikatif.
4. Tema keluhan diidentifikasi dengan pendekatan keyword-based thematic coding agar mudah diterjemahkan ke konteks bisnis.
