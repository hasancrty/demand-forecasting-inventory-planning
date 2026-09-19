from pathlib import Path

import pandas as pd


def read_demand_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Veri dosyasi bulunamadi: {path}")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("Yalnizca CSV veya Excel dosyalari desteklenir.")


def prepare_daily_demand(data: pd.DataFrame) -> pd.DataFrame:
    prepared = data.copy()
    prepared["DATE"] = pd.to_datetime(prepared["DATE"], errors="coerce")
    for column in ("DEMAND", "LEAD_TIME_DAYS", "UNIT_COST"):
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    static = (
        prepared.sort_values("DATE")
        .groupby("ITEM_CODE")[["LEAD_TIME_DAYS", "UNIT_COST"]]
        .last()
    )
    daily = (
        prepared.groupby(["ITEM_CODE", "DATE"], as_index=False)["DEMAND"]
        .sum()
        .sort_values(["ITEM_CODE", "DATE"])
    )

    completed: list[pd.DataFrame] = []
    for item_code, group in daily.groupby("ITEM_CODE"):
        dates = pd.date_range(group["DATE"].min(), group["DATE"].max(), freq="D")
        item = group.set_index("DATE").reindex(dates, fill_value=0).rename_axis("DATE").reset_index()
        item["ITEM_CODE"] = item_code
        item["LEAD_TIME_DAYS"] = static.loc[item_code, "LEAD_TIME_DAYS"]
        item["UNIT_COST"] = static.loc[item_code, "UNIT_COST"]
        completed.append(item)
    return pd.concat(completed, ignore_index=True).sort_values(["ITEM_CODE", "DATE"])

