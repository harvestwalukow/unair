import json
from pathlib import Path

import numpy as np
import pandas as pd


NOTEBOOK = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
RESULT = Path("all_models_complete_case_result.json")


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
        elif "def stratified_split" in normalized:
            exec(
                "def stratified_split" + normalized.split("def stratified_split", 1)[1].split(
                    "\ntrain_idx, test_idx = stratified_split", 1
                )[0],
                namespace,
            )
        elif normalized.startswith("def preprocess_train_test"):
            exec(normalized.split("\nX_train, X_test, feature_names, medians", 1)[0], namespace)
        elif normalized.startswith("def softmax_baseline"):
            exec(normalized.split("B, fit_info =", 1)[0], namespace)
        elif "from sklearn.compose import ColumnTransformer" in normalized:
            exec(
                normalized.split("\nif TREE_MODELS_AVAILABLE:", 1)[0],
                namespace,
            )
    return namespace


def make_confusion(y_true, y_pred, labels):
    confusion = np.zeros((len(labels), len(labels)), dtype=int)
    for actual, predicted in zip(y_true, y_pred):
        confusion[actual, predicted] += 1
    return confusion


def class_metrics(confusion, labels):
    metrics = {}
    for class_index, class_name in enumerate(labels):
        tp = confusion[class_index, class_index]
        fp = confusion[:, class_index].sum() - tp
        fn = confusion[class_index, :].sum() - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        metrics[class_name] = {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "support": int(confusion[class_index, :].sum()),
        }
    return metrics


ns = load_model_namespace()
df_raw = pd.read_csv(ns["CSV_PATH"])
class_order = ns["CLASS_ORDER"]
target = ns["TARGET"]

df_complete_raw = df_raw.dropna(axis=0, how="any").copy()
df_complete = ns["engineer_features"](df_complete_raw)
df_model = df_complete[df_complete[target].isin(class_order)].reset_index(drop=True)
y = pd.Categorical(df_model[target], categories=class_order, ordered=True).codes

train_idx, test_idx = ns["stratified_split"](y, test_size=0.25, seed=42)
X_train, X_test, feature_names, *_ = ns["preprocess_train_test"](df_model, train_idx, test_idx)
y_train, y_test = y[train_idx], y[test_idx]

B, fit_info = ns["fit_multinomial_logit"](
    X_train, y_train, max_iter=80, tol=1e-7, l2=ns["BEST_L2"]
)
y_pred_logit, _ = ns["predict_multinomial"](X_test, B)
conf_logit = make_confusion(y_test, y_pred_logit, class_order)

result = {
    "rows": {
        "original": int(len(df_raw)),
        "complete_case": int(len(df_model)),
        "deleted": int(len(df_raw) - len(df_model)),
    },
    "distribution": df_model[target].value_counts().reindex(class_order).fillna(0).astype(int).to_dict(),
    "split": {"train": int(len(train_idx)), "test": int(len(test_idx))},
    "models": {
        "Multinomial Logistic Regression": {
            "accuracy": float((y_pred_logit == y_test).mean()),
            "confusion": conf_logit.tolist(),
            "metrics": class_metrics(conf_logit, class_order),
            "iterations": int(fit_info["iterations"]),
            "feature_count_with_intercept": int(len(feature_names)),
        }
    },
}


if ns.get("TREE_MODELS_AVAILABLE"):
    ColumnTransformer = ns["ColumnTransformer"]
    RandomForestClassifier = ns["RandomForestClassifier"]
    Pipeline = ns["Pipeline"]
    OneHotEncoder = ns["OneHotEncoder"]
    XGBClassifier = ns["XGBClassifier"]

    def make_tree_preprocessor(num_cols, cat_cols):
        return ColumnTransformer(
            [
                ("num", "passthrough", num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ]
        )

    def eval_tree(model):
        X_train_tree = df_model.iloc[train_idx][ns["PREDICTORS"]]
        X_test_tree = df_model.iloc[test_idx][ns["PREDICTORS"]]
        pipe = Pipeline(
            [
                ("preprocess", make_tree_preprocessor(ns["NUMERIC_PREDICTORS"], ns["CATEGORICAL_PREDICTORS"])),
                ("model", model),
            ]
        )
        pipe.fit(X_train_tree, y_train)
        pred = pipe.predict(X_test_tree)
        confusion = make_confusion(y_test, pred, class_order)
        return {
            "accuracy": float((pred == y_test).mean()),
            "confusion": confusion.tolist(),
            "metrics": class_metrics(confusion, class_order),
        }

    result["models"]["Random Forest"] = eval_tree(
        RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=1,
        )
    )
    result["models"]["XGBoost"] = eval_tree(
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
        )
    )

RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
