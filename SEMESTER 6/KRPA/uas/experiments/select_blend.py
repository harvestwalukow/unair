"""Select Ridge/RF ensemble settings using training-only expanding CV."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from esi_variants import CUTOFF_WEEK, forecast_frame, make_esi


def oof(estimator, x, y, splits):
    actual, pred = [], []
    for tr, va in splits:
        estimator.fit(x.iloc[tr], y.iloc[tr])
        actual.extend(y.iloc[va])
        pred.extend(estimator.predict(x.iloc[va]))
    return np.asarray(actual), np.asarray(pred)


def main():
    raw = pd.read_csv("output/merged_weekly_before_imputation.csv", parse_dates=["week"])
    esi, *_ = make_esi(raw, "clip_gt_0.975")
    frame, features = forecast_frame(esi)
    train = frame.loc[frame["target_week"] < CUTOFF_WEEK].reset_index(drop=True)
    x, y = train[features], train["target"]
    splits = list(TimeSeriesSplit(n_splits=5).split(x))

    ridge_predictions = {}
    for alpha in [0.1, 1.0, 10.0, 100.0, 1000.0]:
        model = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=alpha)),
        ])
        actual, pred = oof(model, x, y, splits)
        ridge_predictions[alpha] = pred

    rf_predictions = {}
    for depth, leaf, max_features in itertools.product([3, 5, None], [2, 8], [0.6, 0.8, 1.0]):
        key = (depth, leaf, max_features)
        model = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(
                n_estimators=150, max_depth=depth, min_samples_leaf=leaf,
                max_features=max_features, random_state=42, n_jobs=1,
            )),
        ])
        actual, pred = oof(model, x, y, splits)
        rf_predictions[key] = pred

    rows = []
    for alpha, ridge_pred in ridge_predictions.items():
        for rf_key, rf_pred in rf_predictions.items():
            for ridge_weight in [0.25, 0.5, 0.75]:
                blend = ridge_weight * ridge_pred + (1 - ridge_weight) * rf_pred
                rows.append({
                    "ridge_alpha": alpha,
                    "rf_max_depth": str(rf_key[0]),
                    "rf_min_samples_leaf": rf_key[1],
                    "rf_max_features": rf_key[2],
                    "ridge_weight": ridge_weight,
                    "cv_rmse": np.sqrt(mean_squared_error(actual, blend)),
                    "cv_r2": r2_score(actual, blend),
                })
    results = pd.DataFrame(rows).sort_values("cv_rmse")
    out = Path("output/experiments")
    out.mkdir(parents=True, exist_ok=True)
    results.to_csv(out / "blend_cv_selection.csv", index=False)
    print(results.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
