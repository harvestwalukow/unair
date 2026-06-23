from pathlib import Path

import numpy as np
import pandas as pd

from main import FORECAST_FEATURES, PCA_FEATURES


OUTPUT = Path("output")


def test_weekly_esi_output_is_complete_and_chronological():
    esi = pd.read_csv(OUTPUT / "esi_dataset.csv", parse_dates=["week"])
    assert len(esi) == 233
    assert esi["week"].is_monotonic_increasing
    assert esi["week"].dt.dayofweek.eq(6).all()
    assert not esi[PCA_FEATURES + ["esi"]].isna().any().any()
    assert (esi["split"].eq("train").sum(), esi["split"].eq("test").sum()) == (186, 47)
    assert esi.loc[esi["split"].eq("test"), "week"].min() == pd.Timestamp("2025-07-27")


def test_forecast_target_is_exactly_next_week_esi():
    forecast = pd.read_csv(
        OUTPUT / "forecast_dataset.csv", parse_dates=["week", "target_week"]
    )
    esi = pd.read_csv(OUTPUT / "esi_dataset.csv", parse_dates=["week"])
    lookup = esi.set_index("week")["esi"]
    expected = forecast["target_week"].map(lookup)
    assert np.allclose(forecast["esi_next_week"], expected)
    assert (forecast["target_week"] > forecast["week"]).all()
    assert not forecast[FORECAST_FEATURES + ["esi_next_week"]].isna().any().any()


def test_model_outputs_and_predictions_are_available():
    results = pd.read_csv(OUTPUT / "model_results.csv")
    predictions = pd.read_csv(OUTPUT / "actual_vs_predicted.csv")
    assert set(results["model"]) == {
        "Naive Forecast",
        "Moving Average 4 Minggu",
        "Linear Regression",
        "Ridge Regression",
        "Random Forest",
        "XGBoost",
        "Ensemble Ridge-Random Forest",
    }
    assert len(predictions) == 46
    assert results.iloc[0]["model"] == "Ensemble Ridge-Random Forest"
    assert results.iloc[0]["r2"] > 0.69
    assert results.iloc[0]["rmse"] < results.loc[
        results["model"].eq("Naive Forecast"), "rmse"
    ].iloc[0]


def test_expected_figures_exist():
    names = [
        "fig_esi_timeseries.png",
        "fig_actual_vs_predicted.png",
        "fig_feature_importance.png",
        "fig_correlation_heatmap.png",
        "fig_pca_explained_variance.png",
    ]
    for name in names:
        path = OUTPUT / "figures" / name
        assert path.exists() and path.stat().st_size > 10_000
