"""Leakage-safe forecasting experiments for improving one-week ESI R-squared.

Candidates are ranked by expanding-window out-of-fold performance on the
training period. The chronological holdout is reported but never used to fit
models or preprocessing.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import ParameterGrid, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


SEED = 42
CUTOFF = pd.Timestamp("2025-07-27")
OUT = Path("output/experiments")


def slope(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    return float(np.polyfit(x, values, 1)[0])


def build_features() -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv("output/esi_dataset.csv", parse_dates=["week"])
    frame = frame.sort_values("week").reset_index(drop=True)

    raw = [
        "esi",
        "x_tweet_volume_log1p",
        "x_negative_sentiment_mean",
        "x_negative_tweet_ratio",
        "gt_harga_naik",
        "gt_biaya_hidup",
        "gt_harga_beras",
        "gt_harga_bbm",
        "gt_phk",
        "gt_mean_score",
        "usd_idr_return",
        "usd_idr_volatility_4w",
        "rupiah_depreciation_dummy",
    ]
    features = list(raw)

    # Lags use only information observable by the end of week t.
    for column in ["esi", "gt_mean_score", "x_negative_sentiment_mean", "usd_idr_return"]:
        for lag in [1, 2, 3, 4, 8]:
            name = f"{column}_lag_{lag}"
            frame[name] = frame[column].shift(lag)
            features.append(name)

    for column in ["esi", "gt_mean_score", "x_negative_sentiment_mean", "usd_idr_return"]:
        for period in [1, 2, 4]:
            name = f"{column}_diff_{period}"
            frame[name] = frame[column].diff(period)
            features.append(name)

    for column in ["esi", "gt_mean_score", "x_negative_sentiment_mean", "usd_idr_return"]:
        for window in [2, 4, 8]:
            mean_name = f"{column}_roll_mean_{window}"
            std_name = f"{column}_roll_std_{window}"
            frame[mean_name] = frame[column].rolling(window).mean()
            frame[std_name] = frame[column].rolling(window).std()
            features.extend([mean_name, std_name])

    frame["esi_slope_4"] = frame["esi"].rolling(4).apply(slope, raw=True)
    frame["gt_mean_slope_4"] = frame["gt_mean_score"].rolling(4).apply(slope, raw=True)
    frame["esi_momentum_x_level"] = frame["esi_diff_1"] * frame["esi"]
    frame["gt_momentum_x_level"] = frame["gt_mean_score_diff_1"] * frame["gt_mean_score"]
    frame["esi_squared"] = frame["esi"] ** 2
    frame["esi_diff_1_squared"] = frame["esi_diff_1"] ** 2
    frame["gt_mean_squared"] = frame["gt_mean_score"] ** 2
    features.extend([
        "esi_slope_4", "gt_mean_slope_4", "esi_momentum_x_level",
        "gt_momentum_x_level", "esi_squared", "esi_diff_1_squared", "gt_mean_squared",
    ])

    week_number = frame["week"].dt.isocalendar().week.astype(float)
    frame["week_sin"] = np.sin(2 * np.pi * week_number / 52.18)
    frame["week_cos"] = np.cos(2 * np.pi * week_number / 52.18)
    frame["time_index"] = np.arange(len(frame), dtype=float)
    features.extend(["week_sin", "week_cos", "time_index"])

    frame["target_week"] = frame["week"].shift(-1)
    frame["target"] = frame["esi"].shift(-1)
    frame["target_delta"] = frame["target"] - frame["esi"]
    frame = frame.dropna(subset=[*features, "target", "target_week"]).reset_index(drop=True)
    return frame, features


def metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "r2": float(r2_score(y, pred)),
    }


def candidate_specs():
    scale = lambda model: Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", model),
    ])
    trees = lambda model: Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", model),
    ])
    return {
        "Ridge": (
            scale(Ridge()),
            {"model__alpha": [0.01, 0.1, 1.0, 10.0, 100.0]},
        ),
        "ElasticNet": (
            scale(ElasticNet(max_iter=20_000, random_state=SEED)),
            {
                "model__alpha": [0.001, 0.01, 0.05, 0.1],
                "model__l1_ratio": [0.1, 0.5, 0.9],
            },
        ),
        "RandomForest": (
            trees(RandomForestRegressor(n_estimators=300, random_state=SEED, n_jobs=1)),
            {
                "model__max_depth": [5, None],
                "model__min_samples_leaf": [2, 8],
                "model__max_features": [0.6, 1.0],
            },
        ),
        "ExtraTrees": (
            trees(ExtraTreesRegressor(n_estimators=300, random_state=SEED, n_jobs=1)),
            {
                "model__max_depth": [5, None],
                "model__min_samples_leaf": [2, 8],
                "model__max_features": [0.6, 1.0],
            },
        ),
        "GradientBoosting": (
            trees(GradientBoostingRegressor(random_state=SEED)),
            {
                "model__n_estimators": [100, 300],
                "model__learning_rate": [0.03, 0.1],
                "model__max_depth": [1, 2],
                "model__min_samples_leaf": [5],
                "model__loss": ["squared_error", "huber"],
            },
        ),
        "HistGradientBoosting": (
            trees(HistGradientBoostingRegressor(random_state=SEED)),
            {
                "model__max_iter": [100, 300],
                "model__learning_rate": [0.03, 0.1],
                "model__max_leaf_nodes": [7, 15],
                "model__l2_regularization": [1.0],
            },
        ),
        "XGBoost": (
            trees(XGBRegressor(
                objective="reg:squarederror", random_state=SEED, n_jobs=1, verbosity=0
            )),
            {
                "model__n_estimators": [100, 300],
                "model__learning_rate": [0.03, 0.1],
                "model__max_depth": [1, 2],
                "model__min_child_weight": [5],
                "model__subsample": [0.8],
                "model__colsample_bytree": [0.8],
                "model__reg_lambda": [1.0, 10.0],
            },
        ),
    }


def tune_candidate(name, estimator, grid, x, y_level, current, mode="level"):
    splitter = TimeSeriesSplit(n_splits=5)
    best = None
    target = y_level if mode == "level" else y_level - current
    for params in ParameterGrid(grid):
        fold_actual = []
        fold_pred = []
        for train_idx, valid_idx in splitter.split(x):
            model = clone(estimator).set_params(**params)
            model.fit(x.iloc[train_idx], target.iloc[train_idx])
            pred = model.predict(x.iloc[valid_idx])
            if mode == "delta":
                pred = pred + current.iloc[valid_idx].to_numpy()
            fold_actual.extend(y_level.iloc[valid_idx].to_numpy())
            fold_pred.extend(pred)
        score = metrics(np.asarray(fold_actual), np.asarray(fold_pred))
        if best is None or score["rmse"] < best["cv"]["rmse"]:
            best = {"params": params, "cv": score}
    final_model = clone(estimator).set_params(**best["params"])
    final_model.fit(x, target)
    return final_model, best


def main():
    frame, features = build_features()
    train = frame.loc[frame["target_week"] < CUTOFF].copy()
    test = frame.loc[frame["week"] >= CUTOFF].copy()
    x_train, y_train = train[features], train["target"]
    x_test, y_test = test[features], test["target"]

    rows = []
    predictions = {"week": test["target_week"], "actual": y_test}
    fitted = {}
    for name, (estimator, grid) in candidate_specs().items():
        for mode in ["level", "delta"]:
            model, best = tune_candidate(
                name, estimator, grid, x_train, y_train, train["esi"], mode=mode
            )
            pred = model.predict(x_test)
            if mode == "delta":
                pred = pred + test["esi"].to_numpy()
            test_score = metrics(y_test.to_numpy(), pred)
            key = f"{name}_{mode}"
            rows.append({
                "candidate": key,
                **{f"cv_{k}": v for k, v in best["cv"].items()},
                **{f"test_{k}": v for k, v in test_score.items()},
                "params": json.dumps(best["params"], sort_keys=True),
            })
            predictions[key] = pred
            fitted[key] = model
            print(key, best["cv"], test_score, best["params"], flush=True)

    results = pd.DataFrame(rows).sort_values("cv_rmse").reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT / "r2_candidate_results.csv", index=False)
    pd.DataFrame(predictions).to_csv(OUT / "r2_candidate_predictions.csv", index=False)
    print("\nRanked by training CV RMSE")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
