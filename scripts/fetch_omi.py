#!/usr/bin/env python3
"""Fetch daily OMI tropospheric NO2 around a few cities. No login needed.

Product  OMI/Aura NO2 Cloud-Screened Total and Tropospheric Column L3 Global Gridded
         0.25 x 0.25 degree, daily (short name OMNO2d, version 003, NASA GES DISC,
         doi:10.5067/Aura/OMI/DATA3007). Field: ColumnAmountNO2TropCloudScreened
         (tropospheric column, pixels with cloud fraction below 30 %).
Copy     NASA's copy in the Registry of Open Data on AWS, bucket "omi-no2-nasa"
         (cloud-optimised GeoTIFF, one file per day, 1 Oct 2004 - 31 May 2020).

Each file is a global grid. We read only the 6 x 6 cells around each city (HTTP range
requests through GDAL), so the whole 16-year record is a few megabytes of traffic.

Output   data/raw/omi_daily_cutouts.npz
           dates   'YYYY-MM-DD' for every calendar day in the period
           status  'ok' or 'missing' (no file for that day in the bucket)
           <city>  float32 [n_days, 6, 6] in molecules/cm2, NaN = no valid retrieval,
                   row 0 is the northernmost row
           west_north  per city: longitude/latitude of the cut-out's north-west corner
         data/raw/MANIFEST.csv   one row per day: file name, size, ETag (MD5) from the bucket
"""
import argparse, csv, datetime as dt, os, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import rasterio
import requests
from rasterio.windows import Window

BUCKET = "https://omi-no2-nasa.s3.amazonaws.com"
RES = 0.25
HALF = 3                      # cut-out is 6 x 6 cells = 1.5 x 1.5 degrees

CITIES = {                    # name: (lat, lon) of the city centre. All 14 regions of Uzbekistan:
    "tashkent": (41.31, 69.28),     # Tashkent city
    "almalyk": (40.85, 69.60),      # Tashkent region (admin centre Nurafshon would overlap the city box)
    "andijan": (40.78, 72.34),      # Andijan region
    "bukhara": (39.77, 64.42),      # Bukhara region
    "fergana": (40.39, 71.78),      # Fergana region
    "jizzakh": (40.12, 67.84),      # Jizzakh region
    "namangan": (41.00, 71.67),     # Namangan region
    "navoi": (40.10, 65.38),        # Navoi region
    "karshi": (38.86, 65.79),       # Kashkadarya region
    "samarkand": (39.65, 66.96),    # Samarkand region
    "gulistan": (40.49, 68.78),     # Syrdarya region
    "termez": (37.22, 67.28),       # Surkhandarya region
    "urgench": (41.55, 60.63),      # Khorezm region
    "nukus": (42.46, 59.60),        # Republic of Karakalpakstan
    # Background (control) boxes: open desert, no town or plant inside the 0.5 deg box
    "bg_kyzylkum_w": (41.50, 62.00),  # Kyzylkum desert, between Urgench and Uchkuduk
    "bg_kyzylkum_e": (42.50, 65.00),  # Kyzylkum desert, north of Navoi region towns
    "bg_ustyurt": (44.00, 57.00),     # Ustyurt plateau
}


def corner(lat, lon):
    """Grid corner (lat, lon) nearest to the city centre. The analysis box is the 2 x 2
    cells that meet at this corner (0.5 x 0.5 degrees)."""
    return round(lat / RES) * RES, round(lon / RES) * RES


def window_for(lat, lon):
    clat, clon = corner(lat, lon)
    col = int(round((clon + 180.0) / RES)) - HALF
    row = int(round((90.0 - clat) / RES)) - HALF
    return Window(col, row, 2 * HALF, 2 * HALF), (clon - HALF * RES, clat + HALF * RES)


def list_bucket():
    """All daily files in the bucket: date -> (key, size, etag)."""
    out, token = {}, None
    while True:
        params = {"list-type": "2", "max-keys": "1000"}
        if token:
            params["continuation-token"] = token
        xml = requests.get(BUCKET + "/", params=params, timeout=60).text
        for key, etag, size in re.findall(
                r"<Key>([^<]+)</Key>.*?<ETag>&quot;([^&]+)&quot;</ETag><Size>(\d+)</Size>", xml):
            m = re.match(r"OMI-Aura_L3-OMNO2d_(\d{4})m(\d\d)(\d\d)_v003-.*\.tif$", key)
            if m:
                out[f"{m.group(1)}-{m.group(2)}-{m.group(3)}"] = (key, int(size), etag)
        m = re.search(r"<NextContinuationToken>([^<]+)<", xml)
        if not m:
            return out
        token = m.group(1)


def read_day(key):
    for attempt in range(6):
        try:
            with rasterio.open(f"/vsicurl/{BUCKET}/{key}") as ds:
                assert ds.width == 1440 and ds.height == 720, "unexpected grid"
                res = {}
                for name, (lat, lon) in CITIES.items():
                    win, _ = window_for(lat, lon)
                    a = ds.read(1, window=win).astype("f4")
                    a[a < -1e29] = np.nan           # fill value is -1.2676506e30
                    res[name] = a
                return res
        except Exception as e:
            last = e
            time.sleep(1 + 2 * attempt)
    raise IOError(f"gave up on {key}: {last}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw = os.path.join(here, "data", "raw")
    os.makedirs(raw, exist_ok=True)

    files = list_bucket()
    first, last = min(files), max(files)
    print(f"bucket has {len(files)} daily files, {first} to {last}", flush=True)
    days, d = [], dt.date.fromisoformat(first)
    while d <= dt.date.fromisoformat(last):
        days.append(d.isoformat())
        d += dt.timedelta(days=1)

    env = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
               GDAL_HTTP_MAX_RETRY="3", GDAL_HTTP_RETRY_DELAY="1")
    ca = os.environ.get("CURL_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if ca:                                            # only needed behind a TLS-inspecting proxy
        env["CURL_CA_BUNDLE"] = ca
        env["GDAL_CURL_CA_BUNDLE"] = ca
    got, t0 = {}, time.time()
    with rasterio.Env(**env):
        with ThreadPoolExecutor(a.workers) as ex:
            fut = {ex.submit(read_day, files[k][0]): k for k in days if k in files}
            for n, f in enumerate(as_completed(fut), 1):
                got[fut[f]] = f.result()
                if n % 500 == 0 or n == len(fut):
                    print(f"  {n}/{len(fut)}  {time.time() - t0:.0f}s", flush=True)

    blank = np.full((2 * HALF, 2 * HALF), np.nan, "f4")
    arrays = {c: np.stack([got[k][c] if k in got else blank for k in days]) for c in CITIES}
    status = np.array(["ok" if k in got else "missing" for k in days])
    np.savez_compressed(os.path.join(raw, "omi_daily_cutouts.npz"), dates=np.array(days), status=status,
                        cities=np.array(list(CITIES)), centres=np.array([CITIES[c] for c in CITIES]),
                        west_north=np.array([window_for(*CITIES[c])[1] for c in CITIES]),
                        res=RES, half=HALF, **arrays)
    with open(os.path.join(raw, "MANIFEST.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "file", "bytes", "etag_md5", "url"])
        for k in days:
            if k in files:
                key, size, etag = files[k]
                w.writerow([k, key, size, etag, f"{BUCKET}/{key}"])
    print(f"saved {len(days)} days, {int((status == 'missing').sum())} without a file")


if __name__ == "__main__":
    main()
