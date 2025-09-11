#!/usr/bin/env python
"""
Télécharge Sentinel‑2 L2A (BOA) depuis Planetary Computer pour une AOI.
- Recherche entre 2024‑01‑01 et 2025‑07‑31 (modifiez au besoin)
- Cloud cover < 20 %
- Choisit automatiquement le produit le plus récent
- Télécharge B04, B05, B08, B8A (.jp2)
"""

import os
import json
import requests
from datetime import datetime
from pystac_client import Client
import planetary_computer as pc
from tqdm import tqdm
from urllib.parse import urlparse

# --- Config ---
AOI_PATH   = "aoi.geojson"
OUT_ROOT   = os.path.join("data", "S2", "L2A")
DATE_RANGE = ("2023-01-01", "2025-09-06")
  # début, fin
MAX_CLOUD  = 60
BANDS      = ["B04", "B05", "B08", "B8A"]

# 1) Charger AOI
with open(AOI_PATH, "r", encoding="utf-8") as f:
    geom = json.load(f)["features"][0]["geometry"]

# 2) STAC search
catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
search = catalog.search(
    collections=["sentinel-2-l2a"],
    intersects=geom,
    datetime=f"{DATE_RANGE[0]}/{DATE_RANGE[1]}",
    query={
    "eo:cloud_cover": {"lt": MAX_CLOUD},
    "sentinel:tile_id": {"eq": "31TCJ"}
},
)


items = list(search.items())
print(f"▶️ {len(items)} L2A product(s) between {DATE_RANGE[0]} and {DATE_RANGE[1]} with cloud<{MAX_CLOUD}%")

if not items:
    raise SystemExit("❌ Aucun L2A trouvé : élargissez la période ou le % nuages.")

# 3) Choisir le plus récent
items.sort(key=lambda it: it.datetime, reverse=True)
item = items[0]
print(f"✓ Choisi : {item.id} — date {item.datetime.date()} — cloud {item.properties['eo:cloud_cover']}%")

# 4) Créer dossier
out_dir = os.path.join(OUT_ROOT, item.id)
os.makedirs(out_dir, exist_ok=True)

# 5) Télécharger les bandes
for b in BANDS:
    asset = item.assets.get(b)
    if asset is None:
        print(f"⚠️ Band {b} not found for this product")
        continue

    # Signer l'URL et nettoyer le nom de fichier
    url = pc.sign(asset.href)
    clean_name = os.path.basename(urlparse(url).path)
    out_fp = os.path.join(out_dir, clean_name)

    if os.path.exists(out_fp):
        print(f"✓ {clean_name} déjà là")
        continue

    # Téléchargement avec barre de progression
    r = requests.get(url, stream=True, timeout=60)
    size = int(r.headers.get("Content-Length", 0) or 0)
    with open(out_fp, "wb") as f, tqdm(
        desc=f"DL {clean_name}",
        total=size, unit="B", unit_scale=True
    ) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                break
            f.write(chunk)
            bar.update(len(chunk))

print("✅ Téléchargement terminé :", out_dir)
