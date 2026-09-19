from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = ("DATE", "ITEM_CODE", "DEMAND", "LEAD_TIME_DAYS", "UNIT_COST")


@dataclass(frozen=True)
class ForecastConfig:
    input_path: Path
    output_dir: Path
    forecast_days: int = 30
    test_days: int = 30
    service_level_z: float = 1.645
    random_seed: int = 42

