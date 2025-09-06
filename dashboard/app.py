# ──────────────────────────────────
# app.py  –  Sentinel‑2 index viewer
# ──────────────────────────────────
import os, glob, datetime as dt, re
import streamlit as st
import rasterio
import numpy as np
import pandas as pd
import leafmap.foliumap as leafmap

st.set_page_config(page_title="🌿 Sentinel‑2 Dashboard", layout="wide")
st.title("Sentinel‑2 Vegetation‑Index Dashboard")

# ───────────────────────────
# 1. Locate available rasters
# ───────────────────────────
ARCHIVE = r"..\data\S2\indices\archive"  # adjust if needed
files_all = sorted(glob.glob(os.path.join(ARCHIVE, "veg_indices_*.tif")))
if not files_all:
    st.error(f"No veg_indices_*.tif files found in {ARCHIVE}")
    st.stop()

# Extract first 8‑digit block (YYYYMMDD) from each filename
files, dates = [], []
for f in files_all:
    m = re.search(r"(\d{8})", os.path.basename(f))
    if m:
        dates.append(dt.datetime.strptime(m.group(1), "%Y%m%d").date())
        files.append(f)
    else:
        st.warning(f"⛔ Date not found in filename, skipping: {f}")

if not files:
    st.error("No valid raster files after filtering.")
    st.stop()

# ──────────────────
# 2. Sidebar controls
# ──────────────────
chosen_date = st.sidebar.date_input(
    "Choose acquisition date",
    value=dates[-1],
    min_value=dates[0],
    max_value=dates[-1],
)
TIF = files[dates.index(chosen_date)]
st.sidebar.write(f"Raster file: `{os.path.basename(TIF)}`")

# ──────────────────────────────
# 3. Helper to display one band
# ──────────────────────────────
def show_band(band_idx, tab, title, cmap, vmin, vmax):
    with tab:
        m = leafmap.Map(center=[34.172, -6.68], zoom=17)
        m.add_raster(
            TIF,
            bands=(band_idx,),
            layer_name=title,
            colormap=cmap,
            vmin=vmin,
            vmax=vmax,
        )

# ─────────────
# 4. Tab layout
# ─────────────
tab_ndvi, tab_ndre, tab_savi = st.tabs(["🌿 NDVI", "🟥 NDRE", "🟠 SAVI"])
show_band(1, tab_ndvi, "NDVI", "RdYlGn", -0.1, 0.9)
show_band(2, tab_ndre, "NDRE", "Viridis", -0.1, 0.6)
show_band(3, tab_savi, "SAVI", "Spectral", -0.1, 0.9)


st.caption("© ESA Copernicus 2025 – Sentinel‑2 L2A processed via Python & GDAL")
