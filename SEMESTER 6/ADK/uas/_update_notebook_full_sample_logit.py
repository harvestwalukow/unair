import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))


def get_source(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def set_source(cell, text):
    cell["source"] = text


def clear_code_output(cell):
    if cell.get("cell_type") == "code":
        cell["execution_count"] = None
        cell["outputs"] = []


for cell in notebook["cells"]:
    source = get_source(cell)

    if source.startswith("## Ringkasan"):
        set_source(
            cell,
            """## Ringkasan

Penelitian ini menganalisis faktor-faktor yang berkaitan dengan tingkat risiko penyakit kardiovaskular pada pasien di Bangladesh menggunakan regresi logistik multinomial. Data yang digunakan adalah CAIR-CVD-2025 yang berisi 1.529 observasi pasien dengan variabel demografis, antropometrik, klinis, biokimia, serta gaya hidup. Variabel respon yang dianalisis adalah tingkat risiko CVD dengan tiga kategori, yaitu rendah, menengah, dan tinggi. Beberapa variabel prediktor yang digunakan meliputi usia, indeks massa tubuh, lingkar perut, tekanan darah sistolik dan diastolik, total kolesterol, HDL, gula darah puasa, estimasi LDL, jenis kelamin, status merokok, status diabetes, aktivitas fisik, serta riwayat keluarga CVD. Analisis dilakukan melalui eksplorasi data, pembersihan nilai hilang dengan complete-case analysis, pembentukan model regresi logistik multinomial menggunakan seluruh data yang lengkap, evaluasi klasifikasi pada data pembentukan model, dan interpretasi odds ratio. Model menggunakan kategori `LOW` sebagai kategori referensi sehingga koefisien dan odds ratio menjelaskan kecenderungan masuk kategori `INTERMEDIARY` atau `HIGH` dibandingkan risiko rendah. Notebook ini juga menghindari penggunaan `CVD Risk Score` sebagai prediktor utama karena variabel tersebut berpotensi menjadi sumber kebocoran informasi terhadap `CVD Risk Level`.

**Kata kunci:** regresi logistik multinomial, penyakit kardiovaskular, odds ratio, klasifikasi, CAIR-CVD-2025.
""",
        )

    elif "## 3.4 Langkah Analisis" in source:
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

Variabel prediktor utama setelah peningkatan model:

- Numerik asli: `Age`, `BMI`, `Abdominal Circumference (cm)`, `Total Cholesterol (mg/dL)`, `HDL (mg/dL)`, `Fasting Blood Sugar (mg/dL)`, `Systolic BP`, `Diastolic BP`, `Estimated LDL (mg/dL)`, `Weight (kg)`, `Height (m)`, dan `Waist-to-Height Ratio`.
- Numerik turunan: `Pulse Pressure` dan `Total_to_HDL_Ratio`.
- Kategorik asli: `Sex`, `Smoking Status`, `Diabetes Status`, `Physical Activity Level`, `Family History of CVD`, dan `Blood Pressure Category`.
- Kategorik turunan: `High_Total_Cholesterol`, `Low_HDL`, `High_Fasting_Blood_Sugar`, `Obesity_Class`, `Age_Group`, `WHtR_High`, `Smoke_Diabetes`, dan `Family_Smoke`.

Variabel `CVD Risk Score` tetap tidak digunakan karena berpotensi menyebabkan kebocoran informasi terhadap `CVD Risk Level`.

## 3.4 Langkah Analisis

1. Memuat dan memeriksa struktur dataset asli.
2. Menghapus seluruh baris yang memiliki minimal satu nilai hilang pada 22 kolom asli (complete-case analysis).
3. Membuat fitur turunan klinis yang masih wajar digunakan sebelum mengetahui label risiko.
4. Mengubah variabel kategorik menjadi dummy variable.
5. Menstandarkan seluruh prediktor numerik/dummy berdasarkan seluruh data complete-case yang digunakan membangun model.
6. Membangun model regresi logistik multinomial ridge dengan kategori referensi `LOW` menggunakan seluruh data complete-case.
7. Mengevaluasi hasil klasifikasi pada data yang sama yang dipakai untuk membangun model.
8. Menginterpretasikan confusion matrix, akurasi, precision, recall, F1-score, koefisien, dan odds ratio.
""",
        )

    elif source.startswith("df_model = df[df[TARGET].isin(CLASS_ORDER)].copy()"):
        set_source(
            cell,
            """df_model = df[df[TARGET].isin(CLASS_ORDER)].reset_index(drop=True).copy()
y = pd.Categorical(df_model[TARGET], categories=CLASS_ORDER, ordered=True).codes

print("Jumlah seluruh data complete-case yang digunakan untuk model:", len(df_model))
display(pd.DataFrame({
    "jumlah": pd.Series(y).map(dict(enumerate(CLASS_ORDER))).value_counts().reindex(CLASS_ORDER),
    "persentase": (pd.Series(y).map(dict(enumerate(CLASS_ORDER))).value_counts().reindex(CLASS_ORDER) / len(df_model) * 100).round(2),
}))
""",
        )
        clear_code_output(cell)

    elif source.startswith("def preprocess_train_test(df, train_idx, test_idx):"):
        set_source(
            cell,
            """def preprocess_full_sample(df):
    X_raw = pd.get_dummies(
        df[PREDICTORS],
        columns=CATEGORICAL_PREDICTORS,
        drop_first=True,
        dtype=float,
    )

    means = X_raw.mean()
    stds = X_raw.std(ddof=0).replace(0, 1)
    X_raw = (X_raw - means) / stds

    X = np.column_stack([np.ones(len(X_raw)), X_raw.to_numpy(float)])
    feature_names = ["Intercept"] + X_raw.columns.tolist()
    return X, feature_names, means, stds

X_all, feature_names, means, stds = preprocess_full_sample(df_model)
y_all = y.copy()

print("Jumlah fitur termasuk intercept:", X_all.shape[1])
print("Regularisasi ridge terbaik yang digunakan:", BEST_L2)
print("Nama fitur:")
display(pd.Series(feature_names))
""",
        )
        clear_code_output(cell)

    elif "B, fit_info = fit_multinomial_logit(X_train, y_train" in source:
        set_source(
            cell,
            """B, fit_info = fit_multinomial_logit(X_all, y_all, max_iter=80, tol=1e-7, l2=BEST_L2)

print("Iterasi konvergensi:", fit_info["iterations"])
print("Negative log-likelihood akhir:", round(float(fit_info["loss"]), 4))
print("L2 regularization:", BEST_L2)
""",
        )
        clear_code_output(cell)

    elif source.startswith("y_pred, y_prob = predict_multinomial(X_test, B)"):
        set_source(
            cell,
            """y_pred, y_prob = predict_multinomial(X_all, B)
class_map = dict(enumerate(CLASS_ORDER))

accuracy = (y_pred == y_all).mean()
print("Akurasi pada seluruh data pembentukan model:", round(float(accuracy), 4))

confusion = pd.crosstab(
    pd.Series(y_all).map(class_map),
    pd.Series(y_pred).map(class_map),
    rownames=["Aktual"],
    colnames=["Prediksi"],
).reindex(index=CLASS_ORDER, columns=CLASS_ORDER, fill_value=0)

display(confusion)
""",
        )
        clear_code_output(cell)

    elif source.startswith("report = classification_report_manual(y_test, y_pred, CLASS_ORDER)"):
        set_source(
            cell,
            """report = classification_report_manual(y_all, y_pred, CLASS_ORDER)
display(report.round(4))
""",
        )
        clear_code_output(cell)

    elif "perubahan satu satuan adalah satu standar deviasi pada data latih" in source:
        set_source(
            cell,
            """## 4.10 Interpretasi Singkat

Cara membaca output:

- Jika odds ratio suatu variabel lebih besar dari 1 pada kolom `HIGH`, maka kenaikan variabel tersebut berasosiasi dengan meningkatnya odds pasien berada pada risiko `HIGH` dibandingkan `LOW`, dengan asumsi variabel lain konstan.
- Jika odds ratio kurang dari 1, maka variabel tersebut berasosiasi dengan menurunnya odds kategori tersebut dibandingkan `LOW`.
- Untuk prediktor numerik, interpretasi berlaku setelah standardisasi. Artinya, perubahan satu satuan adalah satu standar deviasi pada seluruh data complete-case yang dipakai membangun model.
- Untuk prediktor kategorik dummy, interpretasi dibandingkan kategori referensi yang otomatis di-drop saat one-hot encoding.

Catatan penting: interpretasi ini adalah asosiasi statistik, bukan bukti kausal.
""",
        )

    elif "## 4.11 Perbandingan dengan Random Forest dan XGBoost" in source:
        set_source(
            cell,
            """## 4.11 Catatan Evaluasi

Pada versi notebook ini, model regresi logistik multinomial dibangun menggunakan **seluruh 762 data complete-case** tanpa pembagian data latih dan data uji. Karena itu, angka akurasi yang dilaporkan di atas adalah **akurasi pada data pembentukan model** (apparent accuracy), bukan akurasi generalisasi pada data baru.

Pilihan ini sesuai dengan permintaan untuk menggunakan seluruh data dalam pembentukan model. Namun secara metodologis, konsekuensinya adalah performa model pada data baru tidak dapat dievaluasi secara terpisah pada versi notebook ini.
""",
        )

    elif source.startswith("import sys\nfrom pathlib import Path\n\nlocal_deps = Path(\".codex_deps\")"):
        set_source(
            cell,
            """# Perbandingan model lain dihilangkan pada versi ini agar fokus notebook
# tetap konsisten dengan permintaan: seluruh data digunakan untuk membangun
# model regresi logistik multinomial utama tanpa train-test split.
print("Bagian perbandingan model non-logistik tidak dijalankan pada versi full-sample ini.")
""",
        )
        clear_code_output(cell)

    elif source.startswith("**Interpretasi perbandingan:**"):
        set_source(
            cell,
            """**Catatan:** karena seluruh data complete-case digunakan langsung untuk membangun model utama, bagian pembanding berbasis train-test split tidak lagi digunakan pada versi notebook ini. Fokus interpretasi diarahkan pada model regresi logistik multinomial utama dan odds ratio-nya.
""",
        )

    elif "## 4.12 Stress Test untuk Mencapai Akurasi 80%" in source:
        set_source(
            cell,
            """## 4.12 Implikasi Pemakaian Seluruh Data

Pemakaian seluruh data complete-case untuk membangun model memberikan manfaat berupa penggunaan semua informasi yang tersedia dalam estimasi koefisien. Akan tetapi, akurasi yang diperoleh menjadi akurasi pada data yang sama dengan data pembentukan model, sehingga tidak boleh diartikan sebagai kemampuan prediksi pada data baru.

Dengan kata lain, versi notebook ini lebih tepat dipakai untuk:

- membentuk model akhir pada seluruh data lengkap,
- mengestimasi koefisien dan odds ratio,
- mendeskripsikan pola asosiasi antar faktor risiko dan kategori `CVD Risk Level`.

Versi ini kurang tepat bila tujuan utamanya adalah menilai performa generalisasi model.
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
print("Baris dihapus:", len(df_raw) - len(df))
print("Baris complete-case:", len(df))
print("Proporsi data yang dipertahankan (%):", round(len(df) / len(df_raw) * 100, 2))
print("Seluruh 762 data complete-case digunakan untuk membangun model.")
display(complete_case_summary)
""",
        )
        clear_code_output(cell)

    elif source.startswith("probability_table = pd.DataFrame(y_prob, columns=[f\"prob_{label}\" for label in CLASS_ORDER])"):
        set_source(
            cell,
            """probability_table = pd.DataFrame(y_prob, columns=[f"prob_{label}" for label in CLASS_ORDER])
probability_table.insert(0, "aktual", pd.Series(y_all).map(class_map).to_numpy())
probability_table.insert(1, "prediksi", pd.Series(y_pred).map(class_map).to_numpy())
display(probability_table.head(20).round(4))
""",
        )
        clear_code_output(cell)


path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
