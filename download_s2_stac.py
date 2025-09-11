#!/usr/bin/env python
import os, json, requests
from datetime import date
from pystac_client import Client
import planetary_computer
from tqdm import tqdm

# 1) Charger l'AOI
with open("aoi.geojson", "r", encoding="utf-8") as f:
    geom = json.load(f)["features"][0]["geometry"]

# 2) Se connecter au STAC de Microsoft Planetary Computer
catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

# 3) Chercher tous les produits Sentinel-2 L1C en juin 2025, cloud <20%
start = "2025-06-01"
end   = "2025-06-30"
search = catalog.search(
    collections=["sentinel-2-l1c"],
    intersects=geom,
    datetime=f"{start}/{end}",
    query={"eo:cloud_cover": {"lt": 20}},
)
items = list(search.get_items())
print(f"▶️ {len(items)} product(s) found between {start} and {end} (cloud<20%)")
for it in items:
    dt = it.properties["datetime"]
    cc = it.properties.get("eo:cloud_cover", 0)
    print(f"  • {it.id} — {dt} — cloud: {cc:.1f}%")

if not items:
    raise SystemExit("❌ No products found. Adjust date or AOI.")

# 4) Sélectionner celui du 23 juin 2025
chosen = next((it for it in items if "20250623T101031" in it.id), None)
if not chosen:
    raise SystemExit("❌ June 23 tile not found in results.")

print(f"▶️ Downloading bands for {chosen.id}…")

# 5) Préparer le dossier de destination
dl_dir = os.path.join("data", "S2", "L1C", chosen.id)
os.makedirs(dl_dir, exist_ok=True)

# 6) Télécharger B04, B08, B05, B8A
bands = ["B04", "B08", "B05", "B8A"]
for b in bands:
    asset = chosen.assets.get(b)
    if asset is None:
        print(f"⚠️ Band {b} not found for this product")
        continue

    href = planetary_computer.sign(asset.href)
    outp = os.path.join(dl_dir, os.path.basename(href))
    if os.path.exists(outp):
        print(f"✓ {os.path.basename(outp)} already exists")
        continue

    # Stream download with progress bar
    r = requests.get(href, stream=True, timeout=60)
    total = int(r.headers.get("Content-Length", 0))
    with open(outp, "wb") as f, tqdm(
        desc=f"DL {os.path.basename(outp)}",
        total=total, unit="B", unit_scale=True
    ) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

print("✅ Download complete:", dl_dir)
