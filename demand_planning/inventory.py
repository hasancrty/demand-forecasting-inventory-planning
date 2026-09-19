import math

import pandas as pd


def calculate_inventory_policy(
    history: pd.DataFrame,
    forecasts: pd.DataFrame,
    service_level_z: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item_code, item in history.groupby("ITEM_CODE"):
        demand = item["DEMAND"].astype(float)
        lead_time = int(item["LEAD_TIME_DAYS"].iloc[-1])
        unit_cost = float(item["UNIT_COST"].iloc[-1])
        average = float(demand.mean())
        deviation = float(demand.std(ddof=1))
        safety_stock = service_level_z * deviation * math.sqrt(lead_time)
        reorder_point = average * lead_time + safety_stock
        forecast_total = float(
            forecasts.loc[forecasts["ITEM_CODE"] == item_code, "FORECAST"].sum()
        )
        rows.append(
            {
                "ITEM_CODE": item_code,
                "LEAD_TIME_DAYS": lead_time,
                "AVERAGE_DAILY_DEMAND": average,
                "DEMAND_STD": deviation,
                "SAFETY_STOCK": math.ceil(safety_stock),
                "REORDER_POINT": math.ceil(reorder_point),
                "FORECAST_PERIOD_DEMAND": math.ceil(forecast_total),
                "SAFETY_STOCK_VALUE": math.ceil(safety_stock) * unit_cost,
            }
        )
    return pd.DataFrame(rows).sort_values("SAFETY_STOCK_VALUE", ascending=False)

