import json
from pathlib import Path

import numpy as np
import pandas as pd


NOTEBOOK = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
RESULT = Path("logit_original_features_only_result.json")


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
        elif normalized.startswith("def softmax_baseline"):
            exec(normalized, namespace)
        elif normalized.startswith("def classification_report_manual"):
            exec(normalized.split("\nreport =", 1)[0], namespace)
    return namespace


def preprocess_full_sample(df, numeric_predictors, categorical_predictors, predictors):
    x_raw = pd.get_dummies(
        df[predictors],
        columns=categorical_predictors,
        drop_first=True,
        dtype=float,
    )
    means = x_raw.mean()
    stds = x_raw.std(ddof=0).replace(0, 1)
    x_raw = (x_raw - means) / stds
    x = np.column_stack([np.ones(len(x_raw)), x_raw.to_numpy(float)])
    feature_names = ["Intercept"] + x_raw.columns.tolist()
    return x, feature_names


ns = load_model_namespace()
df_raw = pd.read_csv(ns["CSV_PATH"])

target = ns["TARGET"]
class_order = ns["CLASS_ORDER"]
numeric_predictors = [
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
categorical_predictors = [
    "Sex",
    "Smoking Status",
    "Diabetes Status",
    "Physical Activity Level",
    "Family History of CVD",
    "Blood Pressure Category",
]
predictors = numeric_predictors + categorical_predictors

required_columns = predictors + [target]
df_model = df_raw.dropna(subset=required_columns).copy()
df_model = df_model[df_model[target].isin(class_order)].reset_index(drop=True)
y = pd.Categorical(df_model[target], categories=class_order, ordered=True).codes

x_all, feature_names = preprocess_full_sample(
    df_model, numeric_predictors, categorical_predictors, predictors
)
b, fit_info = ns["fit_multinomial_logit"](
    x_all, y, max_iter=80, tol=1e-7, l2=ns["BEST_L2"]
)
y_pred, y_prob = ns["predict_multinomial"](x_all, b)
accuracy = float((y_pred == y).mean())

class_map = dict(enumerate(class_order))
confusion = pd.crosstab(
    pd.Series(y).map(class_map),
    pd.Series(y_pred).map(class_map),
    rownames=["Aktual"],
    colnames=["Prediksi"],
).reindex(index=class_order, columns=class_order, fill_value=0)
report = ns["classification_report_manual"](y, y_pred, class_order)

result = {
    "original_rows": int(len(df_raw)),
    "rows_used": int(len(df_model)),
    "rows_deleted": int(len(df_raw) - len(df_model)),
    "rows_kept_pct": float(len(df_model) / len(df_raw) * 100),
    "cvd_risk_score_missing_but_kept": int(
        df_model["CVD Risk Score"].isna().sum() if "CVD Risk Score" in df_model.columns else 0
    ),
    "predictors_used": predictors,
    "accuracy_full_sample": accuracy,
    "iterations": int(fit_info["iterations"]),
    "feature_count_with_intercept": int(len(feature_names)),
    "class_distribution": df_model[target].value_counts().reindex(class_order).astype(int).to_dict(),
    "confusion_matrix": confusion.values.tolist(),
    "classification_report": report.to_dict(orient="records"),
}

RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
