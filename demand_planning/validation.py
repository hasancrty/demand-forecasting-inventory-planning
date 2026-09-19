import pandas as pd

from .config import REQUIRED_COLUMNS


def validate_demand_data(data: pd.DataFrame, minimum_history: int = 75) -> list[str]:
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Eksik kolonlar: {', '.join(missing)}")
    if data.empty:
        raise ValueError("Veri seti bos.")

    dates = pd.to_datetime(data["DATE"], errors="coerce")
    demand = pd.to_numeric(data["DEMAND"], errors="coerce")
    lead_time = pd.to_numeric(data["LEAD_TIME_DAYS"], errors="coerce")
    unit_cost = pd.to_numeric(data["UNIT_COST"], errors="coerce")
    errors: list[str] = []
    if dates.isna().any():
        errors.append("DATE kolonunda gecersiz veya eksik tarih var.")
    if demand.isna().any() or (demand < 0).any():
        errors.append("DEMAND sayisal ve sifir veya daha buyuk olmalidir.")
    if lead_time.isna().any() or (lead_time <= 0).any():
        errors.append("LEAD_TIME_DAYS sifirdan buyuk olmalidir.")
    if unit_cost.isna().any() or (unit_cost < 0).any():
        errors.append("UNIT_COST negatif olamaz.")
    if errors:
        raise ValueError("Veri dogrulama hatalari:\n- " + "\n- ".join(errors))

    counts = data.assign(DATE=dates).groupby("ITEM_CODE")["DATE"].nunique()
    return [
        f"{item}: yalnizca {count} gunluk gecmis var; tahmin guvenilirligi dusuk olabilir."
        for item, count in counts.items()
        if count < minimum_history
    ]

