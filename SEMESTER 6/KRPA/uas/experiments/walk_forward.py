"""Expanding-window one-step ESI forecasts with fixed train-selected settings."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from esi_variants import CUTOFF_WEEK, forecast_frame, make_esi


SEED = 42
OUT = Path("output/experiments")


def metrics(y, pred):
    return {
        "mae": mean_absolute_error(y, pred),
        "rmse": np.sqrt(mean_squared_error(y, pred)),
        "r2": r2_score(y, pred),
    }


def specs():
    return {
        "Ridge": Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ]),
        "RandomForest": Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(
                n_estimators=150, max_depth=5, min_samples_leaf=8,
                max_features=0.8, random_state=SEED, n_jobs=1,
            )),
        ]),
        "ExtraTrees": Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("model", ExtraTreesRegressor(
                n_estimators=150, max_depth=5, min_samples_leaf=4,
                max_features=0.8, random_state=SEED, n_jobs=1,
            )),
        ]),
        "XGBoost": Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("model", XGBRegressor(
                n_estimators=100, max_depth=2, learning_rate=0.1,
                min_child_weight=5, subsample=0.8, colsample_bytree=0.8,
                reg_lambda=10.0, objective="reg:squarederror",
                random_state=SEED, n_jobs=1, verbosity=0,
            )),
        ]),
    }


def main():
    raw = pd.read_csv("output/merged_weekly_before_imputation.csv", parse_dates=["week"])
    results = []
    pred_frame = None
    for variant in ["clip_gt_0.975"]:
        esi, *_ = make_esi(raw, variant)
        frame, features = forecast_frame(esi)
        base_train = frame.loc[frame["target_week"] < CUTOFF_WEEK].copy()
        test = frame.loc[frame["week"] >= CUTOFF_WEEK].copy().reset_index(drop=True)
        if pred_frame is None:
            pred_frame = test[["week", "target_week", "target"]].copy()
        variant_predictions = {}
        for name, estimator in specs().items():
            predictions = []
            for i in range(len(test)):
                # At week t, all targets through t are observed; the current row targets t+1.
                history = pd.concat([base_train, test.iloc[:i]], ignore_index=True)
                model = clone(estimator)
                model.fit(history[features], history["target"])
                predictions.append(float(model.predict(test.loc[[i], features])[0]))
            result = metrics(test["target"], predictions)
            key = f"{variant}__{name}"
            pred_frame[key] = predictions
            variant_predictions[name] = np.asarray(predictions)
            results.append({"variant": variant, "model": name, **result})
            print(key, result, flush=True)
        for ridge_weight in [0.25, 0.5]:
            blend = (
                ridge_weight * variant_predictions["Ridge"]
                + (1 - ridge_weight) * variant_predictions["RandomForest"]
            )
            model_name = f"RF_Ridge_Blend_{ridge_weight:.2f}"
            result = metrics(test["target"], blend)
            key = f"{variant}__{model_name}"
            pred_frame[key] = blend
            results.append({"variant": variant, "model": model_name, **result})
            print(key, result, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).sort_values("r2", ascending=False).to_csv(
        OUT / "walk_forward_results.csv", index=False
    )
    pred_frame.to_csv(OUT / "walk_forward_predictions.csv", index=False)


if __name__ == "__main__":
    main()
