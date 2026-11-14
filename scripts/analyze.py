#!/usr/bin/env python3
"""Turn the OMI cut-outs into seasonal series, coverage numbers and verdicts.

Rules (see METHOD.md; changes made after the first results are in its change log):
  box        the 2 x 2 cells of 0.25 deg (0.5 x 0.5 deg) that meet at the grid corner
             nearest to the city centre
  valid day  at least 2 of the 4 cells have a cloud-screened retrieval
  seasons    DJF, MAM, JJA, SON (December belongs to the following year's winter)
  season-year needs at least 10 valid days, otherwise it is left out
  season value  season level + mean of the daily anomalies of the valid days, where the
             anomaly is the daily value minus that calendar month's long-term mean. This
             keeps a change in WHICH days were seen from looking like a change in the air.
  trend      Sen slope; Mann-Kendall with Hamed-Rao correction; two-sided 5 % level
  family     the 4 seasons of one city form one family (Benjamini-Hochberg adjusted p)
  own test   RISING / FALLING  adjusted p < 0.05
             NOT PROVEN YET    otherwise; we then report the smallest detectable trend
             TOO LITTLE DATA   fewer than 10 usable season-years
  second source  a published seasonal trend counts as significant when |trend| >= 2 x its
             stated +/- (true whether that +/- is one or two standard errors)
  verdict    first compare like with like: our test on the second source's own years
             (2005-2021) against the second source.
             RISING / FALLING   both significant on those years, same sign, and our full
                                record agrees
             SOURCES DISAGREE   on those years one is significant and the other is not, or the
                                signs differ
             RISING / FALLING,  neither is significant on those years, but our full record is:
               one source only  the trend shows only in years the second source does not cover
             NOT PROVEN YET     neither is significant, on any period
             (with no second source the verdict is our own test, marked "one source only")
"""
import csv, datetime as dt, json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trendstats as ts

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "derived")
SITE = os.path.join(HERE, "docs")

BOX_HALF = 1                 # 2 x 2 cells
MIN_CELLS = 2                # of 4
MIN_DAYS = 10                # valid days per season-year
MIN_YEARS = 10               # season-years needed for a verdict
ALPHA = 0.05
UNIT = 1e15                  # report in 10^15 molecules / cm2
SEASONS = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}
SEASON_NAMES = {"DJF": "Winter", "MAM": "Spring", "JJA": "Summer", "SON": "Autumn"}
CITY_NAMES = {"tashkent": "Tashkent", "almaty": "Almaty", "bishkek": "Bishkek"}

# Published comparison: Sharma et al. (2023), Environ. Sci.: Atmos. 3, 905-918, Table S2.
# Merged OMI (2004-2014) + GOME-2B (2013-2021), Nov 2004 - Mar 2021. Units 1e15 molec/cm2/yr.
# The paper does not say whether +/- is one or two standard errors.
PUBLISHED = {
    "tashkent": {"MAM": (0.29, 0.04), "JJA": (0.37, 0.04), "SON": (0.28, 0.06), "DJF": (-0.13, 0.32)},
    "almaty": {"MAM": (0.04, 0.05), "JJA": (0.10, 0.02), "SON": (-0.04, 0.03), "DJF": (-0.23, 0.11)},
    "bishkek": {"MAM": (0.08, 0.02), "JJA": (0.04, 0.01), "SON": (0.05, 0.02), "DJF": (-0.06, 0.07)},
}


def season_of(date):
    for s, months in SEASONS.items():
        if date.month in months:
            return s, date.year + (1 if date.month == 12 else 0)


def box_daily(cut, half=BOX_HALF, min_cells=None):
    """Daily box mean and number of valid cells from [n, 13, 13] cut-outs."""
    c = cut.shape[1] // 2
    sub = cut[:, c - half:c + half, c - half:c + half].reshape(len(cut), -1)
    n_valid = np.isfinite(sub).sum(1)
    need = min_cells if min_cells is not None else (sub.shape[1] + 1) // 2
    with np.errstate(invalid="ignore"):
        mean = np.where(n_valid >= need, np.nansum(sub, 1) / np.maximum(n_valid, 1), np.nan)
    return mean / UNIT, n_valid


def month_climatology(dates, daily):
    """Long-term mean of the valid daily values for each calendar month (index 1..12)."""
    clim = np.full(13, np.nan)
    months = np.array([d.month for d in dates])
    for m in range(1, 13):
        v = daily[months == m]
        v = v[np.isfinite(v)]
        if len(v):
            clim[m] = v.mean()
    return clim


def seasonal_table(dates, daily, status, clim=None):
    """Per season and year: anomaly-based season value, valid days, days in season."""
    if clim is None:
        clim = month_climatology(dates, daily)
    base = {s: float(np.nanmean([clim[m] for m in months])) for s, months in SEASONS.items()}
    acc = {}
    for d, v, st in zip(dates, daily, status):
        s, y = season_of(d)
        v = v - clim[d.month]
        a = acc.setdefault((s, y), dict(sum=0.0, valid=0, days=0, files=0))
        a["days"] += 1
        if st == "ok":
            a["files"] += 1
        if np.isfinite(v):
            a["sum"] += float(v)
            a["valid"] += 1
    rows = []
    for (s, y), a in sorted(acc.items(), key=lambda kv: (kv[0][1], list(SEASONS).index(kv[0][0]))):
        complete = a["days"] >= 85                # drop the partial first/last season
        mean = base[s] + a["sum"] / a["valid"] if a["valid"] >= MIN_DAYS and complete else float("nan")
        rows.append(dict(season=s, year=y, mean=mean, valid_days=a["valid"], days=a["days"],
                         files=a["files"], complete=complete,
                         coverage=a["valid"] / a["days"] if a["days"] else float("nan")))
    return rows


def verdict_for(res, p_adj):
    if res["n"] < MIN_YEARS:
        return "TOO LITTLE DATA"
    if np.isfinite(p_adj) and p_adj < ALPHA:
        return "RISING" if res["slope"] > 0 else "FALLING"
    return "NOT PROVEN YET"


def combined_verdict(own, pub, own_common):
    """Fixed rule that merges our test with a second source (slope, pm).
    own_common is our own verdict on the second source's period.
    Returns (verdict, one_source_only)."""
    if own == "TOO LITTLE DATA" or pub is None:
        return own, True
    pub_sig = abs(pub[0]) >= 2 * pub[1]
    pub_dir = "RISING" if pub[0] > 0 else "FALLING"
    common_sig = own_common in ("RISING", "FALLING")
    # 1. Compare like with like: our test on the study's own years against the study.
    if common_sig and pub_sig:
        if own_common != pub_dir:
            return "SOURCES DISAGREE", False
        return (own, False) if own == own_common else ("SOURCES DISAGREE", False)
    if common_sig != pub_sig:                         # one clear, the other not, same years
        return "SOURCES DISAGREE", False
    # 2. Neither is clear on the study's years: only our longer record can speak.
    if own in ("RISING", "FALLING"):
        return own, True                              # the trend appears after their record ends
    return "NOT PROVEN YET", False


def centre_cell_daily(cut, centre, west_north, res=0.25):
    """Daily value of the single cell that contains the city centre."""
    lat, lon = centre
    col = int((lon - west_north[0]) / res)
    row = int((west_north[1] - lat) / res)
    return cut[:, row, col] / UNIT


def analyse_city(dates, cut, status, first=None, last=None, half=BOX_HALF, daily=None):
    if daily is None:
        daily, _ = box_daily(cut, half)
    rows = seasonal_table(dates, daily, status)
    out = {}
    for s in SEASONS:
        rs = [r for r in rows if r["season"] == s and r["complete"]
              and (first is None or r["year"] >= first) and (last is None or r["year"] <= last)]
        years = [r["year"] for r in rs]
        vals = [r["mean"] for r in rs]
        res = ts.analyse(years, vals, ALPHA)
        cov = [r["coverage"] for r in rs]
        seen = ts.analyse(years, [r["valid_days"] for r in rs], ALPHA)      # did sampling itself change?
        res.update(season=s, years=years, values=vals,
                   seen_days_trend=dict(slope=seen["slope"], p=seen["p"],
                                        first=rs[0]["valid_days"] if rs else None,
                                        last=rs[-1]["valid_days"] if rs else None),
                   valid_days=[r["valid_days"] for r in rs], coverage=cov,
                   coverage_median=float(np.median(cov)) if cov else float("nan"),
                   coverage_min=float(np.min(cov)) if cov else float("nan"),
                   years_dropped=[r["year"] for r in rs if not np.isfinite(r["mean"])])
        out[s] = res
    padj = ts.benjamini_hochberg([out[s]["p"] for s in SEASONS])
    for s, pa in zip(SEASONS, padj):
        r = out[s]
        r["p_adj"] = float(pa)
        r["own_verdict"] = r["verdict"] = verdict_for(r, pa)
        if r["mean"] and np.isfinite(r["mean"]):       # the same numbers as % of the mean level per decade
            for k in ("slope", "ci_low", "ci_high", "mdt"):
                r[k + "_pct_decade"] = 1000.0 * r[k] / r["mean"]
    return out, rows, daily


def read_giovanni(path):
    """Daily single-cell series exported from NASA Giovanni (see GIOVANNI.md).
    Columns: date, <city>_<nw|ne|sw|se> in molecules/cm2, empty = fill value.
    Returns dates and, per city, an array [n, 2, 2] (row 0 north, column 0 west)."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    gdates = [dt.date.fromisoformat(r[0]) for r in rows[1:]]
    cells = {}
    pos = {"nw": (0, 0), "ne": (0, 1), "sw": (1, 0), "se": (1, 1)}
    for j, name in enumerate(head[1:], 1):
        city, corner = name.rsplit("_", 1)
        a = cells.setdefault(city, np.full((len(gdates), 2, 2), np.nan, "f8"))
        r, c = pos[corner]
        a[:, r, c] = [float(row[j]) if row[j] != "" else np.nan for row in rows[1:]]
    return gdates, cells


def clean(o):
    """Make numpy / NaN values JSON friendly."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else round(float(o), 5)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def main():
    z = np.load(os.path.join(RAW, "omi_daily_cutouts.npz"))
    dates = [dt.date.fromisoformat(str(d)) for d in z["dates"]]
    status = [str(s) for s in z["status"]]
    last_file = max(d for d, s in zip(dates, status) if s == "ok")
    keep = [i for i, d in enumerate(dates) if d <= last_file]
    dates = [dates[i] for i in keep]
    status = [status[i] for i in keep]
    cities = [str(c) for c in z["cities"]]
    cuts = {c: z[c][keep].astype("f8") for c in cities}
    aws_last = dates[-1]

    # Optional extension with the same product read through NASA Giovanni, one grid cell at a time
    giovanni = None
    gpath = os.path.join(RAW, "giovanni_cells.csv")
    if os.path.exists(gpath):
        gdates, gcells = read_giovanni(gpath)
        index = {d: i for i, d in enumerate(dates)}
        both = one_only = 0
        pa, pb = [], []
        for c in cities:
            for gi, d in enumerate(gdates):
                if d in index:
                    a = cuts[c][index[d], 2:4, 2:4]
                    b = gcells[c][gi]
                    fa, fb = np.isfinite(a), np.isfinite(b)
                    both += int((fa & fb).sum())
                    one_only += int((fa ^ fb).sum())
                    pa += list(a[fa & fb])
                    pb += list(b[fa & fb])
        new = [gi for gi, d in enumerate(gdates) if d > aws_last]
        for c in cities:
            ext = np.full((len(new), cuts[c].shape[1], cuts[c].shape[2]), np.nan)
            ext[:, 2:4, 2:4] = gcells[c][new]
            cuts[c] = np.concatenate([cuts[c], ext])
        dates += [gdates[gi] for gi in new]
        status += ["ok"] * len(new)
        last_file = dates[-1]
        pa, pb = np.array(pa), np.array(pb)
        giovanni = dict(first_day=str(gdates[new[0]]), last_day=str(dates[-1]), days=len(new),
                        overlap_first=str(gdates[0]), overlap_last=str(aws_last),
                        overlap_cell_days_both_valid=both, overlap_valid_in_one_only=one_only,
                        overlap_correlation=float(np.corrcoef(pa, pb)[0, 1]),
                        overlap_mean_ratio=float(pb.mean() / pa.mean()),
                        overlap_median_abs_difference_1e15=float(np.median(np.abs(pa - pb)) / UNIT))
        print(f"Giovanni extension: {len(new)} days to {dates[-1]}; overlap {gdates[0]} to {aws_last}: {both} cell-days "
              f"valid in both, {one_only} valid in only one; correlation {giovanni['overlap_correlation']:.4f}, "
              f"mean ratio {giovanni['overlap_mean_ratio']:.4f}, median |difference| "
              f"{giovanni['overlap_median_abs_difference_1e15']:.4f}e15")
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SITE, exist_ok=True)

    result = dict(generated=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                  product="OMI/Aura NO2 Cloud-Screened Tropospheric Column, L3 daily 0.25 deg "
                          "(OMNO2d v003, NASA GES DISC, doi:10.5067/Aura/OMI/DATA3007)",
                  source="https://registry.opendata.aws/omi-no2-nasa/", aws_last_day=str(aws_last),
                  giovanni=giovanni,
                  unit="1e15 molecules/cm2", first_day=str(dates[0]), last_day=str(last_file),
                  rules=dict(box_cells=(2 * BOX_HALF) ** 2, min_cells=MIN_CELLS, min_days=MIN_DAYS,
                             min_years=MIN_YEARS, alpha=ALPHA),
                  season_names=SEASON_NAMES, cities={})

    for city in cities:
        cut = cuts[city]
        full, rows, daily = analyse_city(dates, cut, status)
        same, _, _ = analyse_city(dates, cut, status, first=2005, last=2021)   # the paper's period
        ci = list(z["cities"]).index(city)
        robust = {}
        era = " to 2020 only" if giovanni else ""
        one = centre_cell_daily(cut, z["centres"][ci], z["west_north"][ci])
        variants = [("1 cell (0.25 deg)", dict(daily=one)), ("4 x 4 cells (1.0 deg)" + era, dict(half=2)),
                    ("6 x 6 cells (1.5 deg)" + era, dict(half=3))]
        for label, kw in variants:
            alt, _, _ = analyse_city(dates, cut, status, **kw)
            robust[label] = {s: dict(slope=alt[s]["slope"], slope_pct_decade=alt[s].get("slope_pct_decade"),
                                     p_adj=alt[s]["p_adj"], verdict=alt[s]["own_verdict"]) for s in SEASONS}
        # what the same test said with the record cut at 2020 (the end of the open AWS copy)
        early, _, _ = analyse_city(dates, cut, status, last=2020)
        for s in SEASONS:
            full[s]["until_2020"] = dict(verdict=early[s]["own_verdict"], slope_pct_decade=early[s].get("slope_pct_decade"),
                                         ci_low_pct_decade=early[s].get("ci_low_pct_decade"),
                                         ci_high_pct_decade=early[s].get("ci_high_pct_decade"),
                                         mdt_pct_decade=early[s].get("mdt_pct_decade"), last_year=early[s]["last_year"])
        for s in SEASONS:
            full[s]["one_source"] = True
            pub = PUBLISHED.get(city, {}).get(s)
            if pub:
                ours = same[s]
                lo, hi = pub[0] - 2 * pub[1], pub[0] + 2 * pub[1]
                overlap = (ours["ci_low"] <= hi) and (ours["ci_high"] >= lo)
                same_sign = np.sign(ours["slope"]) == np.sign(pub[0])
                full[s]["verdict"], full[s]["one_source"] = combined_verdict(
                    full[s]["own_verdict"], pub, ours["own_verdict"])
                full[s]["published"] = dict(slope=pub[0], pm=pub[1], significant=bool(abs(pub[0]) >= 2 * pub[1]),
                                            ratio=(pub[0] / ours["slope"]) if ours["slope"] else None,
                                            period="2005-2021", ours_same_period=ours["slope"],
                                            ours_same_period_verdict=ours["own_verdict"],
                                            ours_ci=[ours["ci_low"], ours["ci_high"]],
                                            ours_p=ours["p"], same_sign=bool(same_sign),
                                            intervals_overlap=bool(overlap))
        # per-month climatology of coverage (share of days with a valid box mean)
        month_cov = []
        for m in range(1, 13):
            idx = [i for i, d in enumerate(dates) if d.month == m]
            month_cov.append(float(np.isfinite(daily[idx]).mean()))
        cal = {}                                     # one character per day: 1 seen, 0 not seen, - no file
        for d, v, st in zip(dates, daily, status):
            cal.setdefault(d.year, []).append("-" if st != "ok" else ("1" if np.isfinite(v) else "0"))
        wn = z["west_north"][ci]
        clon, clat = float(wn[0]) + 0.75, float(wn[1]) - 0.75
        result["cities"][city] = dict(name=CITY_NAMES.get(city, city.title()),
                                      centre=[float(v) for v in z["centres"][ci]],
                                      box=dict(west=clon - 0.25, south=clat - 0.25, east=clon + 0.25, north=clat + 0.25),
                                      calendar={str(y): "".join(v) for y, v in cal.items()},
                                      calendar_first_doy=dates[0].timetuple().tm_yday,
                                      seasons=full, robustness=robust, month_coverage=month_cov,
                                      days_total=len(dates), days_valid=int(np.isfinite(daily).sum()))
        with open(os.path.join(OUT, f"{city}_daily_no2.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "no2_trop_1e15_molec_cm2", "file_on_server"])
            for d, v, st in zip(dates, daily, status):
                w.writerow([d, "" if not np.isfinite(v) else f"{v:.4f}", st])
        with open(os.path.join(OUT, f"{city}_seasonal_no2.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["season", "year", "mean_1e15_molec_cm2", "valid_days", "days_in_season", "coverage"])
            for r in rows:
                w.writerow([r["season"], r["year"], "" if not np.isfinite(r["mean"]) else f"{r['mean']:.4f}",
                            r["valid_days"], r["days"], f"{r['coverage']:.3f}"])

    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(clean(result), f, indent=1)
    with open(os.path.join(SITE, "results.js"), "w") as f:
        f.write("window.BULB_AIR = " + json.dumps(clean(result), separators=(",", ":")) + ";\n")

    for city, c in result["cities"].items():
        print(f"\n{c['name']}: {c['days_valid']} of {c['days_total']} days valid "
              f"({100 * c['days_valid'] / c['days_total']:.0f} %)")
        for s, r in c["seasons"].items():
            pub = r.get("published")
            extra = (f" | published {pub['slope']:+.2f}±{pub['pm']:.2f}, ours same period "
                     f"{pub['ours_same_period']:+.3f}") if pub else ""
            sd = r["seen_days_trend"]
            print(f"     seen days {sd['first']}->{sd['last']}, trend {sd['slope']:+.2f}/yr p={sd['p']:.3f}")
            print(f"  {s} n={r['n']:2d} {r['slope_pct_decade']:+5.1f}%/dec slope={r['slope']:+.3f} [{r['ci_low']:+.3f},{r['ci_high']:+.3f}] "
                  f"p={r['p']:.3f} p_adj={r['p_adj']:.3f} mdt={r['mdt']:.3f} "
                  f"cover={100 * r['coverage_median']:.0f}% own={r['own_verdict']} -> {r['verdict']}{' (one source)' if r.get('one_source') else ''}{extra}")


if __name__ == "__main__":
    main()
