# Proje 2: Talep Tahmini ve Stok Planlama

Bu orta seviye proje, urun bazinda gunluk talebi tahmin eder ve tahmin sonuclarini
stok politikasina donusturur. Son `test-days` gun ayrilarak mevsimsel naive,
hareketli ortalama, dogrusal regresyon ve random forest modelleri karsilastirilir.
Her urun icin MAE degeri en dusuk model secilir.

## Gerekli kolonlar

- `DATE`: Gunluk tarih (`YYYY-MM-DD`)
- `ITEM_CODE`: Urun kodu
- `DEMAND`: Talep adedi
- `LEAD_TIME_DAYS`: Tedarik suresi
- `UNIT_COST`: Birim maliyet

## Stok hesaplari

- Emniyet stogu = servis seviyesi z degeri x talep standart sapmasi x karekok(lead time)
- Yeniden siparis noktasi = ortalama gunluk talep x lead time + emniyet stogu

Bu hesap, bagimsiz ve yaklasik normal dagilan gunluk talep varsayimina dayanir.

## Calistirma

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --generate-sample
```

Kendi verinizle:

```powershell
python main.py --input data/talep.csv --forecast-days 30 --test-days 30 --service-level 0.95
```

Testler:

```powershell
pytest -q
```

