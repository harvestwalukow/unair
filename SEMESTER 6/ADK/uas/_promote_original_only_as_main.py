import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))


def get_source(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def set_source(cell, text):
    cell["source"] = text
    if cell.get("cell_type") == "code":
        cell["execution_count"] = None
        cell["outputs"] = []


for cell in notebook["cells"]:
    source = get_source(cell)

    if source.startswith("## Ringkasan"):
        set_source(
            cell,
            """## Ringkasan

Penelitian ini menganalisis faktor-faktor yang berkaitan dengan tingkat risiko penyakit kardiovaskular pada pasien di Bangladesh menggunakan regresi logistik multinomial. Data yang digunakan adalah CAIR-CVD-2025 yang berisi 1.529 observasi pasien dengan variabel demografis, antropometrik, klinis, biokimia, serta gaya hidup. Variabel respon yang dianalisis adalah tingkat risiko CVD dengan tiga kategori, yaitu rendah, menengah, dan tinggi. Variabel prediktor yang digunakan pada model utama dibatasi pada kolom asli dataset tanpa feature engineering, yaitu usia, indeks massa tubuh, lingkar perut, tekanan darah sistolik dan diastolik, total kolesterol, HDL, gula darah puasa, estimasi LDL, berat badan, tinggi badan, rasio lingkar pinggang terhadap tinggi badan, jenis kelamin, status merokok, status diabetes, aktivitas fisik, riwayat keluarga CVD, dan kategori tekanan darah. Analisis dilakukan melalui eksplorasi data, penghapusan baris yang missing hanya pada target atau fitur yang dipakai, pembentukan model regresi logistik multinomial menggunakan seluruh data lengkap yang relevan, evaluasi klasifikasi pada data pembentukan model, dan interpretasi odds ratio. Model menggunakan kategori `LOW` sebagai kategori referensi sehingga koefisien dan odds ratio menjelaskan kecenderungan masuk kategori `INTERMEDIARY` atau `HIGH` dibandingkan risiko rendah. Variabel `CVD Risk Score` tetap tidak digunakan sebagai prediktor utama karena berpotensi menjadi sumber kebocoran informasi terhadap `CVD Risk Level`.

**Kata kunci:** regresi logistik multinomial, penyakit kardiovaskular, odds ratio, klasifikasi, CAIR-CVD-2025.
""",
        )

    elif "Variabel prediktor utama setelah peningkatan model:" in source:
        set_source(
            cell,
            """# BAB III. Metodologi Penelitian

## 3.1 Unit Penelitian

Unit penelitian adalah satu pasien pada dataset CAIR-CVD-2025.

## 3.2 Pengambilan Sampel

Dataset terdiri dari 1.529 sampel pasien yang dikumpulkan di Jamalpur Medical College Hospital, Jamalpur, Bangladesh, pada 20 Januari 2024 sampai 1 Januari 2025.

## 3.3 Variabel Penelitian

Variabel respon:

- `CVD Risk Level`: tingkat risiko penyakit kardiovaskular dengan kategori `LOW`, `INTERMEDIARY`, dan `HIGH`.

Variabel prediktor utama dari kolom asli dataset:

- Numerik: `Age`, `BMI`, `Abdominal Circumference (cm)`, `Total Cholesterol (mg/dL)`, `HDL (mg/dL)`, `Fasting Blood Sugar (mg/dL)`, `Systolic BP`, `Diastolic BP`, `Estimated LDL (mg/dL)`, `Weight (kg)`, `Height (m)`, dan `Waist-to-Height Ratio`.
- Kategorik: `Sex`, `Smoking Status`, `Diabetes Status`, `Physical Activity Level`, `Family History of CVD`, dan `Blood Pressure Category`.

Variabel `CVD Risk Score` tetap tidak digunakan karena berpotensi menyebabkan kebocoran informasi terhadap `CVD Risk Level`.

## 3.4 Langkah Analisis

1. Memuat dan memeriksa struktur dataset asli.
2. Menghapus baris yang memiliki missing value hanya pada variabel respon atau fitur yang benar-benar dipakai model.
3. Menggunakan kolom asli dataset tanpa feature engineering.
4. Mengubah variabel kategorik menjadi dummy variable.
5. Menstandarkan seluruh prediktor numerik/dummy berdasarkan seluruh data yang digunakan membangun model.
6. Membangun model regresi logistik multinomial ridge dengan kategori referensi `LOW` menggunakan seluruh data yang lolos seleksi.
7. Mengevaluasi hasil klasifikasi pada data yang sama yang dipakai untuk membangun model.
8. Menginterpretasikan confusion matrix, akurasi, precision, recall, F1-score, koefisien, dan odds ratio.
""",
        )

    elif source.startswith("NUMERIC_PREDICTORS = ["):
        set_source(
            cell,
            """import math
import numpy as np
import pandas as pd

try:
    from IPython.display import display
except ImportError:
    display = print

pd.set_option("display.max_columns", 120)
pd.set_option("display.width", 160)

CSV_PATH = "CVD Dataset.csv"
TARGET = "CVD Risk Level"
BASELINE_CLASS = "LOW"
CLASS_ORDER = ["LOW", "INTERMEDIARY", "HIGH"]

DESCRIPTIVE_NUMERIC_PREDICTORS = [
    "Age",
    "BMI",
    "Abdominal Circumference (cm)",
    "Total Cholesterol (mg/dL)",
    "HDL (mg/dL)",
    "Fasting Blood Sugar (mg/dL)",
    "Systolic BP",
    "Diastolic BP",
    "Estimated LDL (mg/dL)",
]

DESCRIPTIVE_CATEGORICAL_PREDICTORS = [
    "Sex",
    "Smoking Status",
    "Diabetes Status",
    "Physical Activity Level",
    "Family History of CVD",
]

NUMERIC_PREDICTORS = [
    "Age",
    "BMI",
    "Abdominal Circumference (cm)",
    "Total Cholesterol (mg/dL)",
    "HDL (mg/dL)",
    "Fasting Blood Sugar (mg/dL)",
    "Systolic BP",
    "Diastolic BP",
    "Estimated LDL (mg/dL)",
    "Weight (kg)",
    "Height (m)",
    "Waist-to-Height Ratio",
]

CATEGORICAL_PREDICTORS = [
    "Sex",
    "Smoking Status",
    "Diabetes Status",
    "Physical Activity Level",
    "Family History of CVD",
    "Blood Pressure Category",
]

PREDICTORS = NUMERIC_PREDICTORS + CATEGORICAL_PREDICTORS
BEST_L2 = 0.1
""",
        )

    elif source.startswith("df_raw = pd.read_csv(CSV_PATH)"):
        set_source(
            cell,
            """df_raw = pd.read_csv(CSV_PATH)
required_columns = PREDICTORS + [TARGET]
df = df_raw.dropna(subset=required_columns).reset_index(drop=True).copy()

print("Dimensi data asli:", df_raw.shape)
print("Dimensi data setelah menghapus missing pada fitur yang dipakai:", df.shape)
print("Jumlah baris yang dihapus:", len(df_raw) - len(df))
print("Jumlah baris dengan CVD Risk Score kosong tetapi tetap dipakai:", int(df["CVD Risk Score"].isna().sum()))
display(df.head())
display(pd.DataFrame({"tipe_data": df_raw.dtypes, "missing": df_raw.isna().sum()}))
""",
        )

    elif "Fitur turunan yang ditambahkan pada data complete-case" in source:
        set_source(
            cell,
            """target_counts = df[TARGET].value_counts().reindex(CLASS_ORDER)
target_percent = (target_counts / target_counts.sum() * 100).round(2)

target_summary = pd.DataFrame({
    "jumlah": target_counts,
    "persentase": target_percent
})
display(target_summary)
""",
        )

    elif source.startswith("df_model = df[df[TARGET].isin(CLASS_ORDER)]"):
        set_source(
            cell,
            """df_model = df[df[TARGET].isin(CLASS_ORDER)].reset_index(drop=True).copy()
y = pd.Categorical(df_model[TARGET], categories=CLASS_ORDER, ordered=True).codes

print("Jumlah seluruh data yang digunakan untuk model:", len(df_model))
display(pd.DataFrame({
    "jumlah": pd.Series(y).map(dict(enumerate(CLASS_ORDER))).value_counts().reindex(CLASS_ORDER),
    "persentase": (pd.Series(y).map(dict(enumerate(CLASS_ORDER))).value_counts().reindex(CLASS_ORDER) / len(df_model) * 100).round(2),
}))
""",
        )

    elif "## 4.6 Pemodelan Regresi Logistik Multinomial yang Ditingkatkan" in source:
        set_source(
            cell,
            """## 4.6 Pemodelan Regresi Logistik Multinomial

Model di bawah dibuat dengan parameterisasi baseline-category logit. Kategori referensi adalah `LOW`, sehingga terdapat dua persamaan logit:

- `INTERMEDIARY` dibandingkan `LOW`
- `HIGH` dibandingkan `LOW`

Pada versi utama ini, model dibangun secara lebih sederhana dan transparan:

- Hanya memakai kolom asli dataset tanpa feature engineering.
- Baris dihapus hanya jika target atau fitur yang benar-benar dipakai mengandung missing value.
- `CVD Risk Score` tetap tidak digunakan karena berpotensi langsung menentukan `CVD Risk Level`.
- Menggunakan ridge regularization kecil (`l2 = 0.1`) untuk menjaga kestabilan estimasi.
""",
        )

    elif "seluruh 762 data complete-case" in source:
        set_source(
            cell,
            """## 4.11 Catatan Evaluasi

Pada versi notebook ini, model regresi logistik multinomial dibangun menggunakan **seluruh 845 data** yang memiliki kelengkapan pada target dan fitur yang dipakai. Karena itu, angka akurasi yang dilaporkan di atas adalah **akurasi pada data pembentukan model** (apparent accuracy), bukan akurasi generalisasi pada data baru.

Pilihan ini sesuai dengan permintaan untuk menggunakan seluruh data dalam pembentukan model. Namun secara metodologis, konsekuensinya adalah performa model pada data baru tidak dapat dievaluasi secara terpisah pada versi notebook ini.
""",
        )

    elif "Bagian perbandingan model non-logistik" in source:
        set_source(
            cell,
            """print("Bagian perbandingan model non-logistik tidak dijalankan pada versi utama tanpa feature engineering ini.")""",
        )

    elif source.startswith("**Catatan:** karena seluruh data complete-case"):
        set_source(
            cell,
            """**Catatan:** pada versi utama ini, fokus analisis diarahkan pada model regresi logistik multinomial tanpa feature engineering. Perbandingan dengan model lain tidak dijalankan agar alur notebook tetap konsisten dengan model utama yang dipilih.
""",
        )

    elif "## 4.12 Implikasi Pemakaian Seluruh Data" in source:
        set_source(
            cell,
            """## 4.12 Implikasi Pemakaian Seluruh Data

Pemakaian seluruh data yang lolos seleksi kelengkapan fitur memberikan manfaat berupa penggunaan semua informasi yang relevan dalam estimasi koefisien. Akan tetapi, akurasi yang diperoleh menjadi akurasi pada data yang sama dengan data pembentukan model, sehingga tidak boleh diartikan sebagai kemampuan prediksi pada data baru.

Dengan kata lain, versi notebook ini lebih tepat dipakai untuk:

- membentuk model akhir pada seluruh data yang memenuhi syarat,
- mengestimasi koefisien dan odds ratio,
- mendeskripsikan pola asosiasi antar faktor risiko dan kategori `CVD Risk Level`.

Versi ini kurang tepat bila tujuan utamanya adalah menilai performa generalisasi model.
""",
        )

    elif "## 4.13 Ringkasan Data Complete-Case" in source:
        set_source(
            cell,
            """## 4.13 Ringkasan Data yang Dipakai Model

Model utama pada notebook ini sekarang menggunakan hanya baris yang lengkap pada variabel respon dan fitur asli yang dipakai. Dengan aturan ini, baris dengan `CVD Risk Score` kosong tetap boleh dipertahankan karena variabel tersebut tidak menjadi prediktor model.
""",
        )

    elif source.startswith("complete_case_summary = pd.DataFrame({"):
        set_source(
            cell,
            """complete_case_summary = pd.DataFrame({
    "jumlah": df[TARGET].value_counts().reindex(CLASS_ORDER),
    "persentase": (df[TARGET].value_counts().reindex(CLASS_ORDER) / len(df) * 100).round(2),
})

print("Baris awal:", len(df_raw))
print("Baris yang dipakai model:", len(df))
print("Baris yang dihapus:", len(df_raw) - len(df))
print("Proporsi data yang dipertahankan (%):", round(len(df) / len(df_raw) * 100, 2))
print("Jumlah baris dengan CVD Risk Score kosong tetapi tetap dipakai:", int(df["CVD Risk Score"].isna().sum()))
display(complete_case_summary)
""",
        )

    elif source.startswith("**Interpretasi complete-case:**"):
        set_source(
            cell,
            """**Interpretasi data utama:** setelah hanya menghapus missing value pada target dan fitur yang dipakai, ukuran data yang digunakan menjadi 845 pasien. Pendekatan ini mempertahankan lebih banyak observasi daripada aturan complete-case seluruh kolom. Distribusi kelas tetap menunjukkan `HIGH` sebagai kelas dominan, `INTERMEDIARY` di tengah, dan `LOW` sebagai kelas minoritas.
""",
        )

    elif source.startswith("## 4.14 Eksperimen Tanpa Feature Engineering"):
        set_source(
            cell,
            """## 4.14 Catatan Perubahan Model Utama

Pendekatan tanpa feature engineering yang semula diuji sebagai eksperimen kini dijadikan **model utama** notebook. Alasannya, pendekatan ini lebih sederhana, lebih mudah dijelaskan, tetap menjaga `CVD Risk Score` di luar model, dan mempertahankan lebih banyak data yang valid untuk fitur yang benar-benar digunakan.
""",
        )

    elif source.startswith("original_features_only_numeric = ["):
        set_source(
            cell,
            """print("Pendekatan tanpa feature engineering sudah dijadikan model utama notebook ini.")""",
        )

    elif source.startswith("**Interpretasi eksperimen tanpa feature engineering:**"):
        set_source(
            cell,
            """**Catatan:** hasil tanpa feature engineering kini menjadi hasil utama yang dipakai di seluruh notebook.
""",
        )

    elif "Model ditingkatkan dengan fitur turunan klinis" in source:
        set_source(
            cell,
            """# BAB V. Kesimpulan dan Saran

## 5.1 Kesimpulan

1. Dataset CAIR-CVD-2025 memiliki 1.529 observasi pasien dengan tiga kategori tingkat risiko CVD, yaitu `LOW`, `INTERMEDIARY`, dan `HIGH`.
2. Regresi logistik multinomial sesuai digunakan karena variabel respon memiliki lebih dari dua kategori.
3. Model utama dibangun menggunakan kolom asli dataset tanpa feature engineering dan tanpa `CVD Risk Score` sebagai prediktor.
4. Setelah hanya menghapus baris yang missing pada target atau fitur yang dipakai, model menggunakan 845 observasi.
5. Model akhir tetap menggunakan kategori `LOW` sebagai referensi, sehingga koefisien dan odds ratio menginterpretasikan perbandingan `INTERMEDIARY` vs `LOW` dan `HIGH` vs `LOW`.
6. Evaluasi model dilakukan menggunakan confusion matrix, akurasi, precision, recall, dan F1-score pada data pembentukan model.
7. Odds ratio membantu mengidentifikasi prediktor yang paling kuat berasosiasi dengan kenaikan atau penurunan odds risiko CVD.

## 5.2 Saran

1. Analisis lanjutan dapat membandingkan hasil dengan ordinal logistic regression karena level risiko memiliki urutan alami.
2. Validasi eksternal pada data dari rumah sakit atau wilayah lain diperlukan sebelum model digunakan sebagai alat pendukung keputusan.
3. Variabel `CVD Risk Score` sebaiknya tetap tidak digunakan dalam model prediksi utama karena dapat menyebabkan information leakage jika digunakan untuk memprediksi `CVD Risk Level`.
""",
        )


path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
