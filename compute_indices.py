import rasterio, numpy as np, os

SRC = r"data/S2/indices/stack_aoi.tif"
DST = r"data/S2/indices/veg_indices.tif"

with rasterio.open(SRC) as src:
    red   = src.read(1).astype("float32")   # B04
    redE  = src.read(2).astype("float32")   # B05
    nir   = src.read(3).astype("float32")   # B08
    nirN  = src.read(4).astype("float32")   # B8A

    ndvi = (nir - red) / (nir + red + 1e-6)
    ndre = (nirN - redE) / (nirN + redE + 1e-6)
    savi = 1.5 * (nir - red) / (nir + red + 0.5 + 1e-6)

    meta = src.meta.copy()
    meta.update(count=3, dtype="float32", compress="deflate")

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with rasterio.open(DST, "w", **meta) as dst:
        dst.write(ndvi, 1)
        dst.write(ndre, 2)
        dst.write(savi, 3)

print("✅ NDVI, NDRE, SAVI written to", DST)
