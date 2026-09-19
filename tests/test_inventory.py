import pandas as pd

from demand_planning.inventory import calculate_inventory_policy
from demand_planning.validation import validate_demand_data


def test_inventory_policy_uses_lead_time() -> None:
    history = pd.DataFrame(
        {
            "ITEM_CODE": ["A"] * 4,
            "DEMAND": [8, 10, 12, 10],
            "LEAD_TIME_DAYS": [4] * 4,
            "UNIT_COST": [2.0] * 4,
        }
    )
    forecasts = pd.DataFrame({"ITEM_CODE": ["A"], "FORECAST": [70]})
    result = calculate_inventory_policy(history, forecasts, service_level_z=1.645).iloc[0]
    assert result["REORDER_POINT"] >= 40
    assert result["SAFETY_STOCK"] > 0


def test_negative_demand_is_rejected() -> None:
    data = pd.DataFrame(
        {
            "DATE": ["2025-01-01"],
            "ITEM_CODE": ["A"],
            "DEMAND": [-1],
            "LEAD_TIME_DAYS": [5],
            "UNIT_COST": [10],
        }
    )
    try:
        validate_demand_data(data)
    except ValueError as error:
        assert "DEMAND" in str(error)
    else:
        raise AssertionError("Negatif talep reddedilmeliydi.")
