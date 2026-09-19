import pandas as pd

from .config import ForecastConfig
from .data import prepare_daily_demand, read_demand_data
from .forecasting import forecast_item
from .inventory import calculate_inventory_policy
from .reporting import create_forecast_charts, export_results
from .validation import validate_demand_data


def run_pipeline(config: ForecastConfig) -> dict[str, object]:
    raw = read_demand_data(config.input_path)
    warnings = validate_demand_data(raw, minimum_history=config.test_days + 36)
    prepared = prepare_daily_demand(raw)
    results = [
        forecast_item(
            item_code,
            item,
            config.test_days,
            config.forecast_days,
            config.random_seed,
        )
        for item_code, item in prepared.groupby("ITEM_CODE")
    ]
    forecasts = pd.concat([result.future_forecast for result in results], ignore_index=True)
    metrics = pd.concat([result.metrics for result in results], ignore_index=True)
    test_predictions = pd.concat(
        [result.test_predictions for result in results], ignore_index=True
    )
    inventory_policy = calculate_inventory_policy(
        prepared, forecasts, config.service_level_z
    )
    excel_path = export_results(
        forecasts, metrics, test_predictions, inventory_policy, config.output_dir
    )
    charts = create_forecast_charts(prepared, forecasts, config.output_dir)
    return {
        "excel": excel_path,
        "charts": charts,
        "warnings": warnings,
        "inventory_policy": inventory_policy,
        "selected_models": {
            result.item_code: result.selected_model for result in results
        },
    }

