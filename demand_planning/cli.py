import argparse
from pathlib import Path

from .config import ForecastConfig
from .pipeline import run_pipeline
from .sample_data import generate_sample_data


SERVICE_LEVEL_Z = {0.90: 1.282, 0.95: 1.645, 0.98: 2.054, 0.99: 2.326}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Talep tahmini ve stok planlama")
    parser.add_argument("--input", type=Path, default=Path("data/talep.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--forecast-days", type=int, default=30)
    parser.add_argument("--test-days", type=int, default=30)
    parser.add_argument("--service-level", type=float, choices=SERVICE_LEVEL_Z, default=0.95)
    parser.add_argument("--generate-sample", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.forecast_days <= 0 or args.test_days <= 0:
        raise ValueError("Tahmin ve test gun sayilari sifirdan buyuk olmalidir.")
    if args.generate_sample:
        generate_sample_data(args.input)
        print(f"Ornek veri olusturuldu: {args.input}")
    result = run_pipeline(
        ForecastConfig(
            input_path=args.input,
            output_dir=args.output,
            forecast_days=args.forecast_days,
            test_days=args.test_days,
            service_level_z=SERVICE_LEVEL_Z[args.service_level],
        )
    )
    print("\nSecilen modeller:")
    for item_code, model in result["selected_models"].items():
        print(f"  {item_code}: {model}")
    print("\nStok politikasi:")
    print(result["inventory_policy"].to_string(index=False))
    for warning in result["warnings"]:
        print(f"Uyari: {warning}")
    print(f"Rapor: {result['excel'].resolve()}")

