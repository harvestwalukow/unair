import json
from pathlib import Path

import numpy as np
import pandas as pd


NOTEBOOK = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
RESULT = Path("logit_full_sample_result.json")


def load_model_namespace():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"display": lambda *_args, **_kwargs: None}

    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        normalized = source.lstrip()
        if "CSV_PATH =" in source:
            exec(normalized, namespace)
        elif normalized.startswith("def preprocess_train_test"):
            exec(normalized.split("\nX_train, X_test, feature_names, medians", 1)[0], namespace)
        elif normalized.startswith("def softmax_baseline"):
            exec(normalized.split("B, fit_info =", 1)[0], namespace)
        elif "def classification_report_manual" in normalized:
            exec(normalized.split("\nreport =", 1)[0], namespace)
    return namespace


ns = load_model_namespace()
df_raw = pd.read_csv(ns["CSV_PATH"])
df_complete_raw = df_raw.dropna(axis=0, how="any").copy()
df = ns["engineer_features"](df_complete_raw)
df_model = df[df[ns["TARGET"]].isin(ns["CLASS_ORDER"])].reset_index(drop=True)
y = pd.Categorical(df_model[ns["TARGET"]], categories=ns["CLASS_ORDER"], ordered=True).codes

all_idx = np.arange(len(df_model))
X_full, _, feature_names, *_ = ns["preprocess_train_test"](df_model, all_idx, all_idx)
B, fit_info = ns["fit_multinomial_logit"](
    X_full, y, max_iter=80, tol=1e-7, l2=ns["BEST_L2"]
)
y_pred, y_prob = ns["predict_multinomial"](X_full, B)
accuracy = float((y_pred == y).mean())

class_map = dict(enumerate(ns["CLASS_ORDER"]))
confusion = pd.crosstab(
    pd.Series(y).map(class_map),
    pd.Series(y_pred).map(class_map),
    rownames=["Aktual"],
    colnames=["Prediksi"],
).reindex(index=ns["CLASS_ORDER"], columns=ns["CLASS_ORDER"], fill_value=0)
report = ns["classification_report_manual"](y, y_pred, ns["CLASS_ORDER"])

result = {
    "rows_used": int(len(df_model)),
    "accuracy_full_sample": accuracy,
    "iterations": int(fit_info["iterations"]),
    "feature_count_with_intercept": int(len(feature_names)),
    "class_distribution": df_model[ns["TARGET"]].value_counts().reindex(ns["CLASS_ORDER"]).astype(int).to_dict(),
    "confusion_matrix": confusion.values.tolist(),
    "classification_report": report.to_dict(orient="records"),
}
RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
