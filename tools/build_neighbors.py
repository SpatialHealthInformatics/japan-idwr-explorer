"""Rebuild static/prefecture_neighbors.json from the full-resolution boundaries.

Run locally (needs geopandas and libpysal):
    python tools/build_neighbors.py path/to/japan.geojson
Source file: https://github.com/dataofjapan/land (japan.geojson).
Use the full-resolution file. Simplified polygons drop short borders
(Tochigi-Saitama and Tottori-Hiroshima were lost at tolerance 0.01).
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
from libpysal.weights import Queen, W

src = sys.argv[1]
g = gpd.read_file(src).sort_values("id").reset_index(drop=True).to_crs(6677)
codes = g["id"].astype(int).tolist()
w = Queen.from_dataframe(g, use_index=False, silence_warnings=True)
nb = {codes[i]: set(codes[j] for j in w.neighbors[i]) for i in range(len(codes))}

# island prefectures: link to the nearest prefecture by polygon distance
for i in w.islands:
    d = g.geometry.distance(g.geometry.iloc[i])
    d.iloc[i] = float("inf")
    j = int(d.idxmin())
    nb[codes[i]].add(codes[j])
    nb[codes[j]].add(codes[i])

# Kyushu to Honshu across the Kanmon Strait
nb[40].add(35)
nb[35].add(40)

ww = W({k: sorted(v) for k, v in nb.items()}, silence_warnings=True)
assert ww.n_components == 1 and not ww.islands

out = Path(__file__).resolve().parents[1] / "static" / "prefecture_neighbors.json"
json.dump({"note": "Queen contiguity from full-resolution dataofjapan/land polygons. Added links: "
                   "Hokkaido-Aomori and Okinawa-Kagoshima (nearest prefecture by polygon distance), "
                   "Fukuoka-Yamaguchi (Kanmon Strait). Keys and values are JIS prefecture codes.",
           "neighbors": {str(k): sorted(v) for k, v in nb.items()}},
          open(out, "w"), indent=1)
print("wrote", out)
