#!/usr/bin/env python3
"""Turn the Earthdata Cloud OPeNDAP export (June 2020 - March 2026) into cut-outs like fetch_omi.py.

Why     NASA's open AWS copy of OMNO2d ends in May 2020. Later days come from the same product
        (OMNO2d v003, field ColumnAmountNO2TropCloudScreened) through NASA Earthdata Cloud OPeNDAP,
        which needs a free Earthdata login. GES DISC's old OPeNDAP server was retired.
How     For every daily granule listed by NASA CMR (collection C1266136111-GES_DISC) we requested
        one window over Uzbekistan:
          https://opendap.earthdata.nasa.gov/collections/C1266136111-GES_DISC/granules/<granule>.dap.csv
          ?dap4.ce=/HDFEOS/GRIDS/ColumnAmountNO2/Data_Fields/ColumnAmountNO2TropCloudScreened[500:1:543][940:1:1015]
        Rows 500-543 = cell centres 35.125 to 45.875 N (row 0 is the southernmost row, -89.875),
        columns 940-1015 = 55.125 to 73.875 E. The CSV gives 6 significant digits.
Input   data/raw/opendap_2020_2026.txt: one line per day, "YYYY-MM-DD<TAB>row;row;...", rows from
        south to north, values comma separated, molecules/cm2, fill value -1.26765e+30.
Output  data/raw/omi_daily_cutouts_2020_2026.npz with the same layout as omi_daily_cutouts.npz
        (6 x 6 cells per box, row 0 northernmost), for every box listed in fetch_omi.CITIES.
"""
import os, sys

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
R0, R1, C0, C1 = 500, 543, 940, 1015
RES, HALF = 0.25, 3


def corner(lat, lon):
    return round(lat / RES) * RES, round(lon / RES) * RES


def main():
    from fetch_omi import CITIES          # the same boxes as the AWS part
    raw = os.path.join(HERE, "data", "raw")
    dates, grids = [], []
    with open(os.path.join(raw, "opendap_2020_2026.txt")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d, body = line.split("\t")
            rows = [[float(v) for v in r.split(",")] for r in body.split(";")]
            g = np.array(rows, "f8")
            assert g.shape == (R1 - R0 + 1, C1 - C0 + 1), (d, g.shape)
            g[g < -1e29] = np.nan
            dates.append(d)
            grids.append(g)
    order = np.argsort(dates)
    dates = [dates[i] for i in order]
    grids = np.stack([grids[i] for i in order])
    out = {}
    for name, (lat, lon) in CITIES.items():
        clat, clon = corner(lat, lon)
        # cell centres from north to south and west to east, as in the AWS cut-outs
        lats = clat + RES * (HALF - 0.5) - RES * np.arange(2 * HALF)
        lons = clon - RES * (HALF - 0.5) + RES * np.arange(2 * HALF)
        ri = np.rint((lats + 89.875) / RES).astype(int) - R0
        ci = np.rint((lons + 179.875) / RES).astype(int) - C0
        assert ri.min() >= 0 and ri.max() <= R1 - R0 and ci.min() >= 0 and ci.max() <= C1 - C0, name
        out[name] = grids[:, ri][:, :, ci].astype("f4")
    np.savez_compressed(os.path.join(raw, "omi_daily_cutouts_2020_2026.npz"), dates=np.array(dates),
                        status=np.array(["ok"] * len(dates)), cities=np.array(list(CITIES)), **out)
    print(f"{len(dates)} days, {dates[0]} to {dates[-1]}, {len(CITIES)} boxes")


if __name__ == "__main__":
    main()
