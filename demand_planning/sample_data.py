from pathlib import Path

import numpy as np
import pandas as pd


def generate_sample_data(path: Path, days: int = 540, seed: int = 42) -> Path:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    definitions = {
        "URUN-A": (42, 7, 18.5),
        "URUN-B": (75, 14, 9.8),
        "URUN-C": (24, 21, 44.0),
        "URUN-D": (110, 5, 5.2),
    }
    rows: list[pd.DataFrame] = []
    for index, (item, (base, lead_time, cost)) in enumerate(definitions.items()):
        trend = np.linspace(0, 8 + index * 3, days)
        weekly = 7 * np.sin(2 * np.pi * np.arange(days) / 7 + index)
        yearly = 5 * np.sin(2 * np.pi * np.arange(days) / 365)
        noise = rng.normal(0, 5 + index, days)
        demand = np.maximum(0, np.rint(base + trend + weekly + yearly + noise)).astype(int)
        rows.append(
            pd.DataFrame(
                {
                    "DATE": dates,
                    "ITEM_CODE": item,
                    "DEMAND": demand,
                    "LEAD_TIME_DAYS": lead_time,
                    "UNIT_COST": cost,
                }
            )
        )
    data = pd.concat(rows, ignore_index=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path

