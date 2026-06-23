# Economic Stress Index Forecasting

Pipeline ini membentuk ESI mingguan dari data X, Google Trends, dan USD/IDR,
kemudian memprediksi ESI satu minggu ke depan menggunakan baseline, regresi
linear, Ridge, Random Forest, XGBoost, dan ensemble Ridge–Random Forest.
Evaluasi akhir menggunakan 46 prediksi *expanding walk-forward* dan menghasilkan
R² 0,697 untuk ensemble terbaik.

## Menjalankan ulang

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --stage all --start 2022-01-01 --end 2026-06-20
pytest -q
```

Skor sentimen RoBERTa disimpan di `data/processed/x_sentiment.csv`, sehingga
model bahasa tidak perlu dijalankan ulang kecuali menggunakan
`--force-sentiment`.

## Keluaran utama

- `output/final_dataset.csv`: indikator mingguan setelah imputasi berbasis data latih.
- `output/esi_dataset.csv`: indikator, ESI, dan label periode train/test.
- `output/forecast_dataset.csv`: fitur lag dan target satu minggu ke depan.
- `output/model_results.csv`: MAE, RMSE, R², dan perbaikan terhadap naive.
- `output/actual_vs_predicted.csv`: nilai aktual dan prediksi periode uji.
- `output/pca_loadings.csv`: loading PC1.
- `output/feature_importance.csv`: kepentingan fitur model pohon terbaik.
- `output/run_metadata.json`: sumber, ukuran data, split, parameter, dan metadata eksekusi.
- `output/figures/`: seluruh gambar artikel.
- `ARTIKEL_PKM_ESI.md`: naskah artikel ilmiah.

Data X merupakan 20 hasil `TOP` per bulan dan tidak boleh ditafsirkan sebagai
sampel acak atau volume seluruh platform. Token autentikasi dibaca dari `.env`
dan tidak ditulis ke artefak hasil.

ESI memakai pembatasan persentil ke-97,5 untuk seri Google Trends. Batas,
imputasi, scaler, dan PCA seluruhnya dipelajari hanya dari periode latih.
