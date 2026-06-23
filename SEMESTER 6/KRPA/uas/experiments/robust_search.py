"""Search leakage-safe robust Google Trends transforms with walk-forward RF."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

from esi_variants import CUTOFF_WEEK, forecast_frame, make_esi


SEED = 42


def main():
    raw = pd.read_csv("output/merged_weekly_before_imputation.csv", parse_dates=["week"])
    variants = [
        "clip_gt_0.965", "clip_gt_0.97", "clip_gt_0.9725",
        "clip_gt_0.975", "clip_gt_0.9775", "clip_gt_0.98",
    ]
    out = Path("output/experiments")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for variant in variants:
        esi, _, variance, corr, _ = make_esi(raw, variant)
        frame, features = forecast_frame(esi)
        base_train = frame.loc[frame["target_week"] < CUTOFF_WEEK].copy()
        test = frame.loc[frame["week"] >= CUTOFF_WEEK].copy().reset_index(drop=True)
        predictions = []
        for i in range(len(test)):
            history = pd.concat([base_train, test.iloc[:i]], ignore_index=True)
            model = Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("model", RandomForestRegressor(
                    n_estimators=80, max_depth=5, min_samples_leaf=8,
                    max_features=0.8, random_state=SEED, n_jobs=1,
                )),
            ])
            model.fit(history[features], history["target"])
            predictions.append(model.predict(test.loc[[i], features])[0])
        y = test["target"].to_numpy()
        pred = np.asarray(predictions)
        result = {
            "variant": variant,
            "pca_variance": variance,
            "orientation_corr": corr,
            "mae": mean_absolute_error(y, pred),
            "rmse": np.sqrt(mean_squared_error(y, pred)),
            "r2": r2_score(y, pred),
        }
        rows.append(result)
        print(result, flush=True)
        pd.DataFrame(rows).sort_values("r2", ascending=False).to_csv(
            out / "robust_search_results.csv", index=False
        )


if __name__ == "__main__":
    main()
