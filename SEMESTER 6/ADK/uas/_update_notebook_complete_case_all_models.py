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

    if "## 3.4 Langkah Analisis" in source:
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
5. Menstandarkan seluruh prediktor numerik/dummy berdasarkan data latih.
6. Membagi data menjadi data latih dan uji secara stratifikasi.
7. Membangun model regresi logistik multinomial ridge dengan kategori referensi `LOW`.
8. Mengevaluasi model menggunakan confusion matrix, akurasi, precision, recall, dan F1-score.
9. Membandingkan hasil model utama dengan Random Forest dan XGBoost pada data complete-case yang sama.
10. Menginterpretasikan koefisien dan odds ratio.
""",
        )

    elif source.startswith("df_raw = pd.read_csv(CSV_PATH)\ndf = engineer_features(df_raw)"):
        set_source(
            cell,
            """df_raw = pd.read_csv(CSV_PATH)
df_complete_raw = df_raw.dropna(axis=0, how="any").copy()
df = engineer_features(df_complete_raw)

print("Dimensi data asli:", df_raw.shape)
print("Dimensi data setelah complete-case:", df_complete_raw.shape)
print("Jumlah baris yang dihapus:", len(df_raw) - len(df_complete_raw))
display(df.head())
display(pd.DataFrame({"tipe_data": df_raw.dtypes, "missing": df_raw.isna().sum()}))

engineered_columns = [
    "Pulse Pressure",
    "Total_to_HDL_Ratio",
    "High_Total_Cholesterol",
    "Low_HDL",
    "High_Fasting_Blood_Sugar",
    "Obesity_Class",
    "Age_Group",
    "WHtR_High",
    "Smoke_Diabetes",
    "Family_Smoke",
]
print("Fitur turunan yang ditambahkan pada data complete-case:")
display(df[engineered_columns].head())
""",
        )
        clear_code_output(cell)

    elif source.startswith("def preprocess_train_test(df, train_idx, test_idx):"):
        set_source(
            cell,
            """def preprocess_train_test(df, train_idx, test_idx):
    train = df.iloc[train_idx].copy()
    test = df.iloc[test_idx].copy()

    X_train_raw = pd.get_dummies(
        train[PREDICTORS],
        columns=CATEGORICAL_PREDICTORS,
        drop_first=True,
        dtype=float,
    )
    X_test_raw = pd.get_dummies(
        test[PREDICTORS],
        columns=CATEGORICAL_PREDICTORS,
        drop_first=True,
        dtype=float,
    )
    X_test_raw = X_test_raw.reindex(columns=X_train_raw.columns, fill_value=0.0)

    means = X_train_raw.mean()
    stds = X_train_raw.std(ddof=0).replace(0, 1)
    X_train_raw = (X_train_raw - means) / stds
    X_test_raw = (X_test_raw - means) / stds

    X_train = np.column_stack([np.ones(len(X_train_raw)), X_train_raw.to_numpy(float)])
    X_test = np.column_stack([np.ones(len(X_test_raw)), X_test_raw.to_numpy(float)])
    feature_names = ["Intercept"] + X_train_raw.columns.tolist()

    return X_train, X_test, feature_names, None, None, means, stds

X_train, X_test, feature_names, medians, modes, means, stds = preprocess_train_test(df_model, train_idx, test_idx)
y_train, y_test = y[train_idx], y[test_idx]

print("Jumlah fitur termasuk intercept:", X_train.shape[1])
print("Regularisasi ridge terbaik yang digunakan:", BEST_L2)
print("Nama fitur:")
display(pd.Series(feature_names))
""",
        )
        clear_code_output(cell)

    elif "Bagian ini hanya digunakan sebagai pembanding model." in source:
        set_source(
            cell,
            """## 4.11 Perbandingan dengan Random Forest dan XGBoost

Bagian ini digunakan sebagai pembanding model pada **dataset complete-case** yang sama. Model utama penelitian tetap **regresi logistik multinomial** karena sesuai dengan topik UAS. Random Forest dan XGBoost dipakai untuk melihat apakah model non-linear berbasis pohon dapat menghasilkan akurasi yang lebih tinggi setelah semua baris dengan missing value dihapus.

Perbandingan tetap tidak menggunakan `CVD Risk Score` agar tidak terjadi information leakage.
""",
        )

    elif source.startswith("import sys\nfrom pathlib import Path\n\nlocal_deps = Path(\".codex_deps\")"):
        set_source(
            cell,
            """import sys
from pathlib import Path

local_deps = Path(".codex_deps").resolve()
if local_deps.exists() and str(local_deps) not in sys.path:
    sys.path.insert(0, str(local_deps))

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from xgboost import XGBClassifier
    TREE_MODELS_AVAILABLE = True
except ImportError as exc:
    TREE_MODELS_AVAILABLE = False
    print("Random Forest/XGBoost comparison skipped because package is missing:", exc)

if TREE_MODELS_AVAILABLE:
    def make_tree_preprocessor(num_cols, cat_cols):
        return ColumnTransformer([
            ("num", "passthrough", num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ])

    def evaluate_tree_model(model_name, model):
        X_train_tree = df_model.iloc[train_idx][PREDICTORS]
        X_test_tree = df_model.iloc[test_idx][PREDICTORS]
        pipe = Pipeline([
            ("preprocess", make_tree_preprocessor(NUMERIC_PREDICTORS, CATEGORICAL_PREDICTORS)),
            ("model", model),
        ])
        pipe.fit(X_train_tree, y_train)
        pred = pipe.predict(X_test_tree)
        return {
            "model": model_name,
            "accuracy": accuracy_score(y_test, pred),
            "confusion": pd.DataFrame(
                confusion_matrix(y_test, pred, labels=[0, 1, 2]),
                index=CLASS_ORDER,
                columns=CLASS_ORDER,
            ),
            "report": pd.DataFrame(
                classification_report(y_test, pred, target_names=CLASS_ORDER, output_dict=True, zero_division=0)
            ).T,
        }

    comparison_results = []
    comparison_results.append({
        "model": "Multinomial Logistic Regression",
        "accuracy": accuracy,
        "confusion": confusion,
        "report": report.set_index("kelas"),
    })
    comparison_results.append(evaluate_tree_model(
        "Random Forest",
        RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=1,
        ),
    ))
    comparison_results.append(evaluate_tree_model(
        "XGBoost",
        XGBClassifier(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=5,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=1,
        ),
    ))

    comparison_summary = pd.DataFrame([
        {"model": item["model"], "accuracy": item["accuracy"]}
        for item in comparison_results
    ]).sort_values("accuracy", ascending=False)

    display(comparison_summary.round(4))

    for item in comparison_results:
        print(f"\\n{item['model']}")
        print("Accuracy:", round(float(item["accuracy"]), 4))
        display(item["confusion"])
""",
        )
        clear_code_output(cell)

    elif source.startswith("**Interpretasi perbandingan:**"):
        set_source(
            cell,
            """**Interpretasi perbandingan:** pada dataset complete-case dengan pembagian data yang sama, regresi logistik multinomial tetap menghasilkan akurasi tertinggi, yaitu sekitar 70,68%. Random Forest dan XGBoost sama-sama berada di sekitar 68,59%, sehingga belum melampaui model logistik. Hasil ini mendukung pemilihan regresi logistik multinomial sebagai model utama karena akurasinya paling baik pada uji ini dan interpretasinya tetap paling sesuai untuk Analisis Data Kategorik melalui odds ratio.
""",
        )

    elif "## 4.12 Stress Test untuk Mencapai Akurasi 80%" in source:
        set_source(
            cell,
            """## 4.12 Stress Test untuk Mencapai Akurasi 80%

Setelah seluruh model dialihkan ke **dataset complete-case**, target akurasi 80% masih belum tercapai. Ringkasan hasil pada pembagian data yang sama adalah sebagai berikut:

| Pendekatan | Akurasi Uji | Catatan |
|---|---:|---|
| Regresi logistik multinomial utama | 70.68% | Model utama, complete-case, tanpa `CVD Risk Score` |
| Random Forest | 68.59% | Complete-case, tanpa `CVD Risk Score` |
| XGBoost | 68.59% | Complete-case, tanpa `CVD Risk Score` |

Artinya, penghapusan baris missing memang membantu meningkatkan akurasi model logistik dibanding versi imputasi sebelumnya, tetapi peningkatannya tetap terbatas. Dengan evaluasi yang jujur pada data uji terpisah, target 80% belum bisa dicapai dari kombinasi fitur dan ukuran sampel ini. Untuk melaporkan akurasi 80%, biasanya dibutuhkan praktik yang tidak disarankan, seperti data leakage, tuning berdasarkan data uji, atau pelaporan akurasi data latih.
""",
        )

    elif "## 4.13 Analisis Complete-Case" in source:
        set_source(
            cell,
            """## 4.13 Ringkasan Data Complete-Case

Seluruh model pada notebook ini sekarang menggunakan data **complete-case**, yaitu hanya pasien yang memiliki nilai lengkap pada seluruh 22 kolom asli. Bagian ini merangkum dampak pembersihan data tersebut terhadap ukuran sampel dan distribusi kelas.
""",
        )

    elif source.startswith("# strict complete-case experiment"):
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
print("Semua model di atas menggunakan data complete-case ini.")
display(complete_case_summary)
""",
        )
        clear_code_output(cell)

    elif source.startswith("**Interpretasi complete-case:**"):
        set_source(
            cell,
            """**Interpretasi complete-case:** setelah penghapusan seluruh baris yang memiliki missing value, ukuran data turun dari 1.529 menjadi 762 pasien. Distribusi kelas tetap mirip dengan data asli: `HIGH` tetap paling dominan, `INTERMEDIARY` berada di tengah, dan `LOW` tetap menjadi kelas minoritas. Karena itu, walaupun akurasi model utama meningkat, tantangan utama klasifikasi kelas `LOW` masih tetap ada.
""",
        )


path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
