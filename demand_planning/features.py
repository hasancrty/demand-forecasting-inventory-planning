import numpy as np
import pandas as pd


FEATURE_COLUMNS = (
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_7",
    "rolling_28",
    "day_of_week_sin",
    "day_of_week_cos",
    "trend",
)


def build_features(series: pd.Series) -> pd.DataFrame:
    values = series.astype(float)
    frame = pd.DataFrame(index=values.index)
    frame["lag_1"] = values.shift(1)
    frame["lag_7"] = values.shift(7)
    frame["lag_14"] = values.shift(14)
    frame["rolling_7"] = values.shift(1).rolling(7).mean()
    frame["rolling_28"] = values.shift(1).rolling(28).mean()
    day_of_week = frame.index.dayofweek
    frame["day_of_week_sin"] = np.sin(2 * np.pi * day_of_week / 7)
    frame["day_of_week_cos"] = np.cos(2 * np.pi * day_of_week / 7)
    frame["trend"] = np.arange(len(frame))
    frame["target"] = values
    return frame.dropna()


def features_for_next_date(history: pd.Series, date: pd.Timestamp) -> pd.DataFrame:
    history = history.astype(float)
    row = {
        "lag_1": history.iloc[-1],
        "lag_7": history.iloc[-7],
        "lag_14": history.iloc[-14],
        "rolling_7": history.iloc[-7:].mean(),
        "rolling_28": history.iloc[-28:].mean(),
        "day_of_week_sin": np.sin(2 * np.pi * date.dayofweek / 7),
        "day_of_week_cos": np.cos(2 * np.pi * date.dayofweek / 7),
        "trend": len(history),
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)

