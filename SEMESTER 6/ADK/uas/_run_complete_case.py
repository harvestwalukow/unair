import json
from pathlib import Path

import numpy as np
import pandas as pd


NOTEBOOK = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
RESULT = Path("complete_case_result.json")


def load_model_namespace():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"display": lambda *_args, **_kwargs: None}
    wanted_definitions = (
        "def engineer_features",
        "def stratified_split",
        "def preprocess_train_test",
        "def softmax_baseline",
    )

    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        normalized_source = source.lstrip()
        if "CSV_PATH =" in source or "def stratified_split" in source or normalized_source.startswith(wanted_definitions):
            tree_source = normalized_source
            # Keep definitions/constants, but remove each cell's experiment calls.
            if "def stratified_split" in normalized_source:
                tree_source = "def stratified_split" + normalized_source.split("def stratified_split", 1)[1]
                tree_source = tree_source.split("\ntrain_idx, test_idx = stratified_split", 1)[0]
            elif normalized_source.startswith("def preprocess_train_test"):
                tree_source = normalized_source.split("\nX_train, X_test, feature_names, medians", 1)[0]
            elif normalized_source.startswith("def softmax_baseline"):
                tree_source = normalized_source.split("B, fit_info =", 1)[0]
            exec(tree_source, namespace)
    return namespace


ns = load_model_namespace()
df_raw = pd.read_csv(ns["CSV_PATH"])
class_order = ns["CLASS_ORDER"]
target = ns["TARGET"]

# Strict complete-case analysis: every original column must be observed.
df_complete_raw = df_raw.dropna(axis=0, how="any").copy()
df_complete = ns["engineer_features"](df_complete_raw)
df_complete = df_complete[df_complete[target].isin(class_order)].reset_index(drop=True)
y = pd.Categorical(df_complete[target], categories=class_order, ordered=True).codes

train_idx, test_idx = ns["stratified_split"](y, test_size=0.25, seed=42)
X_train, X_test, feature_names, *_ = ns["preprocess_train_test"](
    df_complete, train_idx, test_idx
)
y_train, y_test = y[train_idx], y[test_idx]
B, fit_info = ns["fit_multinomial_logit"](
    X_train, y_train, max_iter=80, tol=1e-7, l2=ns["BEST_L2"]
)
y_pred, _ = ns["predict_multinomial"](X_test, B)

confusion = np.zeros((len(class_order), len(class_order)), dtype=int)
for actual, predicted in zip(y_test, y_pred):
    confusion[actual, predicted] += 1

metrics = {}
for class_index, class_name in enumerate(class_order):
    tp = confusion[class_index, class_index]
    fp = confusion[:, class_index].sum() - tp
    fn = confusion[class_index, :].sum() - tp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    metrics[class_name] = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": int(confusion[class_index, :].sum()),
    }

result = {
    "original_rows": int(len(df_raw)),
    "complete_rows": int(len(df_complete)),
    "deleted_rows": int(len(df_raw) - len(df_complete)),
    "retained_pct": float(len(df_complete) / len(df_raw) * 100),
    "original_distribution": df_raw[target].value_counts().reindex(class_order).fillna(0).astype(int).to_dict(),
    "complete_distribution": df_complete[target].value_counts().reindex(class_order).fillna(0).astype(int).to_dict(),
    "train_rows": int(len(train_idx)),
    "test_rows": int(len(test_idx)),
    "accuracy": float((y_pred == y_test).mean()),
    "macro_f1": float(np.mean([item["f1"] for item in metrics.values()])),
    "confusion_matrix": confusion.tolist(),
    "class_metrics": metrics,
    "iterations": int(fit_info["iterations"]),
    "feature_count_with_intercept": int(len(feature_names)),
}
RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
