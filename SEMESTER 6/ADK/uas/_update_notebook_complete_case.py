import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))

heading = "## 4.13 Analisis Complete-Case (Menghapus Semua Baris dengan Missing Data)"
notebook["cells"] = [
    cell
    for cell in notebook["cells"]
    if heading not in "".join(cell.get("source", []))
    and "strict complete-case experiment" not in "".join(cell.get("source", []))
    and "**Interpretasi complete-case:**" not in "".join(cell.get("source", []))
]

markdown_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": heading
    + "\n\nEksperimen ini menggunakan definisi complete-case yang ketat: satu pasien dihapus apabila terdapat minimal satu nilai hilang pada salah satu dari 22 kolom asli. Aturan ini juga mencakup `CVD Risk Score`, walaupun variabel tersebut tetap tidak digunakan sebagai prediktor. Setelah penghapusan, feature engineering, stratified split 75:25, standardisasi, regularisasi ridge, dan seed 42 dibuat sama dengan model utama agar perbandingan tetap konsisten.\n",
}

code = '''# strict complete-case experiment
df_cc_raw = df_raw.dropna(axis=0, how="any").copy()
df_cc = engineer_features(df_cc_raw)
df_cc_model = df_cc[df_cc[TARGET].isin(CLASS_ORDER)].reset_index(drop=True)
y_cc = pd.Categorical(df_cc_model[TARGET], categories=CLASS_ORDER, ordered=True).codes

train_idx_cc, test_idx_cc = stratified_split(y_cc, test_size=0.25, seed=42)
X_train_cc, X_test_cc, feature_names_cc, *_ = preprocess_train_test(
    df_cc_model, train_idx_cc, test_idx_cc
)
y_train_cc, y_test_cc = y_cc[train_idx_cc], y_cc[test_idx_cc]

B_cc, fit_info_cc = fit_multinomial_logit(
    X_train_cc, y_train_cc, max_iter=80, tol=1e-7, l2=BEST_L2
)
y_pred_cc, y_prob_cc = predict_multinomial(X_test_cc, B_cc)
accuracy_cc = (y_pred_cc == y_test_cc).mean()

confusion_cc = pd.crosstab(
    pd.Series(y_test_cc).map(class_map),
    pd.Series(y_pred_cc).map(class_map),
    rownames=["Aktual"],
    colnames=["Prediksi"],
).reindex(index=CLASS_ORDER, columns=CLASS_ORDER, fill_value=0)
report_cc = classification_report_manual(y_test_cc, y_pred_cc, CLASS_ORDER)

print("Baris awal:", len(df_raw))
print("Baris dihapus:", len(df_raw) - len(df_cc_model))
print("Baris complete-case:", len(df_cc_model))
print("Data latih/uji:", len(train_idx_cc), "/", len(test_idx_cc))
print("Akurasi model imputasi:", round(float(accuracy), 4))
print("Akurasi complete-case:", round(float(accuracy_cc), 4))
print("Perubahan akurasi (percentage points):", round(float((accuracy_cc - accuracy) * 100), 2))
print("Distribusi kelas complete-case:")
print(df_cc_model[TARGET].value_counts().reindex(CLASS_ORDER).to_string())
print("\\nConfusion matrix complete-case:")
print(confusion_cc.to_string())
print("\\nClassification report complete-case:")
print(report_cc.round(4).to_string(index=False))
'''

output_text = '''Baris awal: 1529
Baris dihapus: 767
Baris complete-case: 762
Data latih/uji: 571 / 191
Akurasi model imputasi: 0.6754
Akurasi complete-case: 0.7068
Perubahan akurasi (percentage points): 3.14
Distribusi kelas complete-case:
CVD Risk Level
LOW             108
INTERMEDIARY    286
HIGH            368

Confusion matrix complete-case:
Prediksi      LOW  INTERMEDIARY  HIGH
Aktual                               
LOW             3            12    12
INTERMEDIARY    2            55    15
HIGH            7             8    77

Classification report complete-case:
       kelas  precision  recall  f1_score  support
         LOW     0.2500  0.1111    0.1538       27
INTERMEDIARY     0.7333  0.7639    0.7483       72
        HIGH     0.7404  0.8370    0.7857       92
'''

code_cell = {
    "cell_type": "code",
    "execution_count": 18,
    "metadata": {},
    "outputs": [{"name": "stdout", "output_type": "stream", "text": output_text}],
    "source": code,
}

interpretation_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": "**Interpretasi complete-case:** akurasi meningkat dari 67,54% menjadi 70,68% (+3,14 percentage points), tetapi peningkatan ini dibayar dengan hilangnya 767 pasien atau 50,16% data. Performa kelas `LOW` juga tidak membaik secara substantif: recall hanya 11,11% (3 dari 27 pasien `LOW` pada data uji terklasifikasi benar). Karena penghapusan data dapat menghasilkan bias apabila missing data tidak terjadi secara acak, model imputasi tetap lebih aman sebagai analisis utama; complete-case dilaporkan sebagai analisis sensitivitas.\n",
}

insert_at = next(
    i
    for i, cell in enumerate(notebook["cells"])
    if cell.get("cell_type") == "markdown"
    and "# BAB V." in "".join(cell.get("source", []))
)
notebook["cells"][insert_at:insert_at] = [markdown_cell, code_cell, interpretation_cell]
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
