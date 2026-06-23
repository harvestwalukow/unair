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

    if source.startswith("def classification_report_manual(y_true, y_pred, labels):"):
        set_source(
            cell,
            """def classification_report_manual(y_true, y_pred, labels):
    rows = []
    for i, label in enumerate(labels):
        tp = np.sum((y_true == i) & (y_pred == i))
        fp = np.sum((y_true != i) & (y_pred == i))
        fn = np.sum((y_true == i) & (y_pred != i))
        support = np.sum(y_true == i)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        rows.append([label, precision, recall, f1, support])
    return pd.DataFrame(rows, columns=["kelas", "precision", "recall", "f1_score", "support"])

report = classification_report_manual(y_all, y_pred, CLASS_ORDER)
display(report.round(4))
""",
        )

    elif source.startswith("coef = pd.DataFrame(B, index=feature_names, columns=CLASS_ORDER[1:])"):
        set_source(
            cell,
            """coef = pd.DataFrame(B, index=feature_names, columns=CLASS_ORDER[1:])

p = X_all.shape[1]
K_minus_1 = len(CLASS_ORDER) - 1
covariance = fit_info["covariance"]
se_flat = np.sqrt(np.maximum(np.diag(covariance), 0))
se = se_flat.reshape(K_minus_1, p).T
se_df = pd.DataFrame(se, index=feature_names, columns=CLASS_ORDER[1:])

z_df = coef / se_df.replace(0, np.nan)
erfc_vec = np.vectorize(math.erfc)
pvalue_df = pd.DataFrame(
    erfc_vec(np.abs(z_df.to_numpy(float)) / math.sqrt(2)),
    index=feature_names,
    columns=CLASS_ORDER[1:],
)

odds_ratio = np.exp(coef)

coef_table = (
    coef.stack().rename("coef")
    .to_frame()
    .join(se_df.stack().rename("std_error"))
    .join(z_df.stack().rename("z_value"))
    .join(pvalue_df.stack().rename("p_value"))
    .join(odds_ratio.stack().rename("odds_ratio"))
    .reset_index()
    .rename(columns={"level_0": "variabel", "level_1": "kategori_vs_LOW"})
)

display(coef_table.round(4))
""",
        )


path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
