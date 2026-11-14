"""Build map/data.js for the 3D map: real per-cell OMI season means + trend results.

Cells: the 6x6 grid of 0.25 deg OMNO2d cells around each box (row 0 = north).
Cell value = mean of valid daily values in that season (10^15 molec/cm2);
null if fewer than 10 valid days. Trend numbers are copied from docs/results.js.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = os.path.join(HERE, "data", "raw")
z1 = np.load(os.path.join(raw, "omi_daily_cutouts.npz"), allow_pickle=True)
z2 = np.load(os.path.join(raw, "omi_daily_cutouts_2020_2026.npz"), allow_pickle=True)
names = [str(c) for c in z1["cities"]]
wn = {n: [float(x) for x in z1["west_north"][i]] for i, n in enumerate(names)}
dates = np.concatenate([z1["dates"], z2["dates"]]).astype("datetime64[D]")
months = (dates.astype("datetime64[M]").astype(int) % 12) + 1
years = dates.astype("datetime64[Y]").astype(int) + 1970
SEAS = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}
sy = years + (months == 12)
LAST = {"DJF": 2026, "MAM": 2025, "JJA": 2025, "SON": 2025}

t = open(os.path.join(HERE, "docs", "results.js")).read()
R = json.loads(t[t.index("{"):t.rindex("}") + 1])

grids = {}
for n in names:
    a = np.concatenate([z1[n], z2[n]]).reshape(len(dates), 36) / 1e15
    g = {}
    for s, ms in SEAS.items():
        ins = np.isin(months, ms)
        g[s] = {}
        for y in range(2005, LAST[s] + 1):
            sel = ins & (sy == y)
            sub = a[sel]
            cnt = np.isfinite(sub).sum(0)
            with np.errstate(invalid="ignore"):
                m = np.nanmean(np.where(np.isfinite(sub), sub, np.nan), 0) if sel.any() else np.full(36, np.nan)
            vals = [None if (c < 10 or not np.isfinite(v)) else round(float(v), 2) for v, c in zip(m, cnt)]
            g[s][y] = {"v": vals, "n": [int(c) for c in cnt], "days": int(sel.sum())}
    grids[n] = g

keep = ["verdict", "own_verdict", "one_source", "slope", "intercept", "ci_low", "ci_high", "p_adj",
        "slope_pct_decade", "ci_low_pct_decade", "ci_high_pct_decade", "mdt_pct_decade", "years", "values",
        "valid_days", "coverage", "coverage_median", "change_point", "until_2020", "published", "mean"]
cities = {}
for k, c in R["cities"].items():
    se = {}
    for s, d in c["seasons"].items():
        e = {x: d.get(x) for x in keep}
        ex = d.get("excess") or {}
        e["excess"] = {x: ex.get(x) for x in ["verdict", "slope", "intercept", "slope_pct_decade",
                                               "ci_low_pct_decade", "ci_high_pct_decade", "years", "values"]}
        se[s] = e
    cities[k] = {"name": c["name"], "region": c["region"], "centre": c["centre"], "box": c["box"],
                 "flag_seasons": c["flag_seasons"], "seasons": se}
bg = {"boxes": R["background"]["boxes"],
      "seasons": {s: {x: d.get(x) for x in ["years", "values", "slope", "intercept", "slope_pct_decade"]}
                  for s, d in R["background"]["seasons"].items()}}
out = {"generated": R["generated"], "product": R["product"], "first_day": R["first_day"],
       "last_day": R["last_day"], "extension": R["extension"], "west_north": wn, "res": 0.25,
       "cities": cities, "background": bg, "grids": grids, "family_size": R["family_size"]}
with open(os.path.join(HERE, "map", "data.js"), "w") as f:
    f.write("window.MAPDATA = " + json.dumps(out, separators=(",", ":"), allow_nan=False) + ";\n")
print("ok", os.path.getsize(os.path.join(HERE, "map", "data.js")))
