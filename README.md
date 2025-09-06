# crop-health-monitoring
# Crop Health Monitoring (Sentinel-2)

Tools to turn Sentinel-2 L2A imagery into vegetation index maps (NDVI, NDRE, SAVI) for precision agriculture. Designed for small-to-medium fields with simple, reproducible steps on Windows, macOS, or Linux.

## ✨ What it does
- Downloads or ingests Sentinel-2 **Level-2A** products (surface reflectance).
- Resamples/aligns key bands to **10 m**.
- Stacks Red, Red-edge, NIR bands into a single raster.
- Computes **NDVI**, **NDRE**, **SAVI** and exports GeoTIFFs.
- (Optional) Clips outputs to your **AOI** (GeoJSON/Shape) and produces basic stats.

## 🧠 Background (short)
- Sentinel-2 MSI has 13 spectral bands (10–60 m). For crop vigor & early stress:
  - **B04 (Red, 10 m)**, **B08 (NIR, 10 m)** → NDVI  
  - **B05 (Red-edge, 20 m)**, **B8A (Narrow NIR, 20 m)** → NDRE  
- We resample B05 and B8A to **10 m** so all math is pixel-aligned.
<img width="945" height="532" alt="Image" src="https://github.com/user-attachments/assets/54282101-d93d-42ee-8472-b41defd49208" />

_(For a concise domain overview used to shape this pipeline, see the attached internship report.)_ :contentReference[oaicite:0]{index=0}

## 📂 Project structure
      ├─ data/
      │ ├─ S2/
      │ │ └─ L2A/<product_id>/
      │ └─ indices/
      │ ├─ R10m_tif/ # resampled 10 m bands live here
      │ └─ outputs/ # final indices + clipped rasters
      ├─ aoi/
      │ └─ aoi.geojson
      ├─ scripts/
      │ ├─ compute_indices.py
      │ └─ utils.py
      ├─ environment.yml
      └─ README.md

## 🛠️ Requirements
- Python 3.10+ (Conda recommended)
- GDAL, Rasterio, Numpy, GeoPandas, Shapely
- (Optional) QGIS for visualization

Create the environment:
```bash
conda env create -f environment.yml
conda activate s2_agro




