from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_forecast_charts(
    history: pd.DataFrame,
    forecasts: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    chart_dir = output_dir / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for item_code, future in forecasts.groupby("ITEM_CODE"):
        past = history[history["ITEM_CODE"] == item_code].tail(90)
        figure, axis = plt.subplots(figsize=(10, 5))
        axis.plot(past["DATE"], past["DEMAND"], label="Gerceklesen", color="#2F6B8A")
        axis.plot(future["DATE"], future["FORECAST"], label="Tahmin", color="#C44E52")
        axis.set(title=f"{item_code} Talep Tahmini", ylabel="Talep", xlabel="Tarih")
        axis.legend()
        axis.grid(alpha=0.2)
        figure.tight_layout()
        path = chart_dir / f"{item_code}_tahmin.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def export_results(
    forecasts: pd.DataFrame,
    metrics: pd.DataFrame,
    test_predictions: pd.DataFrame,
    inventory_policy: pd.DataFrame,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    forecasts.to_csv(output_dir / "gelecek_tahminleri.csv", index=False, date_format="%Y-%m-%d")
    inventory_policy.to_csv(output_dir / "stok_politikasi.csv", index=False)
    excel_path = output_dir / "talep_stok_raporu.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        inventory_policy.to_excel(writer, sheet_name="Stok Politikasi", index=False)
        forecasts.to_excel(writer, sheet_name="Tahminler", index=False)
        metrics.to_excel(writer, sheet_name="Model Karsilastirma", index=False)
        test_predictions.to_excel(writer, sheet_name="Test Sonuclari", index=False)
        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for cells in worksheet.columns:
                worksheet.column_dimensions[cells[0].column_letter].width = min(
                    max(len(str(cell.value or "")) for cell in cells) + 2, 26
                )
    return excel_path

