import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))


def make_markdown_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def make_code_cell(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text,
    }


heading = "## 4.14 Eksperimen Tanpa Feature Engineering"
notebook["cells"] = [
    cell for cell in notebook["cells"]
    if heading not in "".join(cell.get("source", []))
    and "original_features_only_numeric" not in "".join(cell.get("source", []))
    and "**Interpretasi eksperimen tanpa feature engineering:**" not in "".join(cell.get("source", []))
]

markdown_1 = make_markdown_cell(
    heading
    + "\n\nEksperimen ini dibuat untuk menjawab skenario yang lebih sederhana: model hanya memakai **kolom asli dari dataset** tanpa feature engineering. Baris dihapus hanya jika terdapat missing value pada **target** atau pada **fitur yang benar-benar dipakai**. Dengan aturan ini, baris dengan `CVD Risk Score` kosong tetap boleh dipakai karena `CVD Risk Score` memang tidak menjadi prediktor.\n"
)

code = """original_features_only_numeric = [
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

original_features_only_categorical = [
    "Sex",
    "Smoking Status",
    "Diabetes Status",
    "Physical Activity Level",
    "Family History of CVD",
    "Blood Pressure Category",
]

original_features_only_predictors = (
    original_features_only_numeric + original_features_only_categorical
)
original_required_columns = original_features_only_predictors + [TARGET]

df_original_only = (
    df_raw.dropna(subset=original_required_columns)
    .loc[lambda d: d[TARGET].isin(CLASS_ORDER)]
    .reset_index(drop=True)
    .copy()
)
y_original_only = pd.Categorical(
    df_original_only[TARGET], categories=CLASS_ORDER, ordered=True
).codes

X_original_only_raw = pd.get_dummies(
    df_original_only[original_features_only_predictors],
    columns=original_features_only_categorical,
    drop_first=True,
    dtype=float,
)
means_original_only = X_original_only_raw.mean()
stds_original_only = X_original_only_raw.std(ddof=0).replace(0, 1)
X_original_only_raw = (X_original_only_raw - means_original_only) / stds_original_only
X_original_only = np.column_stack(
    [np.ones(len(X_original_only_raw)), X_original_only_raw.to_numpy(float)]
)
feature_names_original_only = ["Intercept"] + X_original_only_raw.columns.tolist()

B_original_only, fit_info_original_only = fit_multinomial_logit(
    X_original_only, y_original_only, max_iter=80, tol=1e-7, l2=BEST_L2
)
y_pred_original_only, y_prob_original_only = predict_multinomial(
    X_original_only, B_original_only
)
accuracy_original_only = (y_pred_original_only == y_original_only).mean()

confusion_original_only = pd.crosstab(
    pd.Series(y_original_only).map(class_map),
    pd.Series(y_pred_original_only).map(class_map),
    rownames=["Aktual"],
    colnames=["Prediksi"],
).reindex(index=CLASS_ORDER, columns=CLASS_ORDER, fill_value=0)
report_original_only = classification_report_manual(
    y_original_only, y_pred_original_only, CLASS_ORDER
)

print("Baris asli dataset:", len(df_raw))
print("Baris yang dipakai:", len(df_original_only))
print("Baris yang dihapus:", len(df_raw) - len(df_original_only))
print("Persentase baris yang dipakai (%):", round(len(df_original_only) / len(df_raw) * 100, 2))
print("Jumlah baris dengan CVD Risk Score kosong tetapi tetap dipakai:", int(df_original_only["CVD Risk Score"].isna().sum()))
print("Jumlah fitur setelah dummy encoding + intercept:", len(feature_names_original_only))
print("Akurasi tanpa feature engineering:", round(float(accuracy_original_only), 4))
print("Akurasi model utama saat ini:", round(float(accuracy), 4))
print("Selisih akurasi (tanpa FE - model utama):", round(float(accuracy_original_only - accuracy), 4))
print("\\nDistribusi kelas:")
display(pd.DataFrame({
    "jumlah": df_original_only[TARGET].value_counts().reindex(CLASS_ORDER),
    "persentase": (df_original_only[TARGET].value_counts().reindex(CLASS_ORDER) / len(df_original_only) * 100).round(2),
}))
print("\\nConfusion matrix:")
display(confusion_original_only)
print("\\nClassification report:")
display(report_original_only.round(4))
"""

markdown_2 = make_markdown_cell(
    "**Interpretasi eksperimen tanpa feature engineering:** model ini memakai 18 kolom asli sebagai prediktor, mempertahankan 845 baris, dan tetap mengizinkan `CVD Risk Score` kosong selama fitur yang dipakai lengkap. Hasilnya, akurasi apparent menjadi sekitar 68,28%, sedikit lebih rendah daripada model utama saat ini yang memakai feature engineering pada 762 baris complete-case penuh (sekitar 68,90%). Jadi, menghapus feature engineering memang membuat model lebih sederhana dan mempertahankan lebih banyak data, tetapi pada eksperimen ini tidak memberi kenaikan akurasi.\n"
)

insert_at = next(
    i
    for i, cell in enumerate(notebook["cells"])
    if cell.get("cell_type") == "markdown"
    and "# BAB V." in "".join(cell.get("source", []))
)
notebook["cells"][insert_at:insert_at] = [markdown_1, make_code_cell(code), markdown_2]

path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
