from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .features import FEATURE_COLUMNS, build_features, features_for_next_date


@dataclass
class ItemForecastResult:
    item_code: str
    selected_model: str
    metrics: pd.DataFrame
    test_predictions: pd.DataFrame
    future_forecast: pd.DataFrame


def _candidate_predictions(train: pd.Series, test: pd.Series, seed: int) -> dict[str, np.ndarray]:
    history = pd.concat([train, test])
    feature_frame = build_features(history)
    training_rows = feature_frame.index <= train.index.max()
    test_rows = feature_frame.index.isin(test.index)
    x_train = feature_frame.loc[training_rows, FEATURE_COLUMNS]
    y_train = feature_frame.loc[training_rows, "target"]
    x_test = feature_frame.loc[test_rows, FEATURE_COLUMNS]

    linear = LinearRegression().fit(x_train, y_train)
    forest = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=2,
        random_state=seed,
        n_jobs=-1,
    ).fit(x_train, y_train)
    naive = history.shift(7).reindex(test.index).to_numpy()
    moving_average = history.shift(1).rolling(28).mean().reindex(test.index).to_numpy()
    return {
        "seasonal_naive": np.clip(naive, 0, None),
        "moving_average_28": np.clip(moving_average, 0, None),
        "linear_regression": np.clip(linear.predict(x_test), 0, None),
        "random_forest": np.clip(forest.predict(x_test), 0, None),
    }


def _fit_selected_model(name: str, history: pd.Series, seed: int):
    if name not in {"linear_regression", "random_forest"}:
        return None
    frame = build_features(history)
    if name == "linear_regression":
        return LinearRegression().fit(frame[list(FEATURE_COLUMNS)], frame["target"])
    return RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=2,
        random_state=seed,
        n_jobs=-1,
    ).fit(frame[list(FEATURE_COLUMNS)], frame["target"])


def _recursive_forecast(
    history: pd.Series,
    model_name: str,
    model,
    forecast_days: int,
) -> pd.DataFrame:
    extended = history.copy().astype(float)
    rows: list[dict[str, object]] = []
    for _ in range(forecast_days):
        date = extended.index.max() + pd.Timedelta(days=1)
        if model_name == "seasonal_naive":
            prediction = extended.iloc[-7]
        elif model_name == "moving_average_28":
            prediction = extended.iloc[-28:].mean()
        else:
            prediction = float(model.predict(features_for_next_date(extended, date))[0])
        prediction = max(0.0, prediction)
        extended.loc[date] = prediction
        rows.append({"DATE": date, "FORECAST": prediction})
    return pd.DataFrame(rows)


def forecast_item(
    item_code: str,
    item_data: pd.DataFrame,
    test_days: int,
    forecast_days: int,
    seed: int,
) -> ItemForecastResult:
    series = item_data.set_index("DATE")["DEMAND"].sort_index().astype(float)
    if len(series) <= test_days + 35:
        raise ValueError(f"{item_code}: en az {test_days + 36} gunluk veri gerekli.")
    train, test = series.iloc[:-test_days], series.iloc[-test_days:]
    predictions = _candidate_predictions(train, test, seed)

    metric_rows: list[dict[str, object]] = []
    for name, predicted in predictions.items():
        metric_rows.append(
            {
                "ITEM_CODE": item_code,
                "MODEL": name,
                "MAE": mean_absolute_error(test, predicted),
                "RMSE": mean_squared_error(test, predicted) ** 0.5,
                "MAPE": np.mean(np.abs((test.to_numpy() - predicted) / np.maximum(test.to_numpy(), 1))) * 100,
            }
        )
    metrics = pd.DataFrame(metric_rows).sort_values("MAE")
    selected = str(metrics.iloc[0]["MODEL"])
    fitted_model = _fit_selected_model(selected, series, seed)
    future = _recursive_forecast(series, selected, fitted_model, forecast_days)
    future["ITEM_CODE"] = item_code
    future["MODEL"] = selected
    test_predictions = pd.DataFrame(
        {
            "DATE": test.index,
            "ITEM_CODE": item_code,
            "ACTUAL": test.to_numpy(),
            "PREDICTED": predictions[selected],
            "MODEL": selected,
        }
    )
    return ItemForecastResult(item_code, selected, metrics, test_predictions, future)

