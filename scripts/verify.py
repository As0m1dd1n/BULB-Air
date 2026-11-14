#!/usr/bin/env python3
"""Three checks anyone can run. Exits with an error if one fails.

  1. Our Mann-Kendall / Sen code against the independent `pymannkendall` package
     (pip install pymannkendall) on 300 random autocorrelated series.
  2. The browser statistics (docs/stats.js, needs Node.js) against the Python results
     for every city and season.
  3. A fresh run of analyze.py against the committed data/derived/results.json.
"""
import json, os, subprocess, sys

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
import trendstats as ts

ok = True


def report(name, passed, detail):
    global ok
    ok = ok and passed
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")


# 1 ------------------------------------------------------------------------------------
try:
    import pymannkendall as pmk
    rng = np.random.default_rng(1)
    worst_slope = worst_p = 0.0
    stricter = 0
    for _ in range(300):
        n = int(rng.integers(8, 25))
        years = np.arange(2005, 2005 + n)
        e = np.zeros(n)
        phi = rng.uniform(0, 0.7)
        for i in range(1, n):
            e[i] = phi * e[i - 1] + rng.normal()
        x = rng.uniform(-0.3, 0.3) * np.arange(n) + e
        with np.errstate(invalid="ignore"):
            ref = pmk.hamed_rao_modification_test(x)
        mine = ts.mann_kendall(years, x)
        slope, _ = ts.sen_slope(years, x)
        worst_slope = max(worst_slope, abs(slope - ref.slope))
        if np.isfinite(ref.p):
            if mine["correction"] == 1.0 and mine["p"] > ref.p + 1e-9:
                stricter += 1          # our rule: the correction may never make the test more lenient
            else:
                worst_p = max(worst_p, abs(mine["p"] - ref.p))
    report("Python vs pymannkendall", worst_slope < 1e-9 and worst_p < 0.01,
           f"largest slope difference {worst_slope:.1e}, largest p difference {worst_p:.4f}; "
           f"{stricter} series where our stricter correction rule gives a larger p")
except ImportError:
    print("[SKIP] Python vs pymannkendall: pymannkendall is not installed")

# 2 ------------------------------------------------------------------------------------
js = r"""
const S = require(process.argv[1] + '/docs/stats.js');
const r = require(process.argv[1] + '/data/derived/results.json');
let worst = 0, n = 0;
const ps = [], refs = [];
for (const c of Object.values(r.cities)) {
  for (const k of Object.keys(c.seasons)) {
    const s = c.seasons[k], a = S.analyse(s.years, s.values);
    ps.push(a.p); refs.push(s.p_adj);
    for (const f of ['slope', 'ci_low', 'ci_high', 'p', 'mdt']) { worst = Math.max(worst, Math.abs(a[f] - s[f])); n++; }
  }
}
const adj = S.benjaminiHochberg(ps);          // one family across all city-season tests
adj.forEach((v, i) => { worst = Math.max(worst, Math.abs(v - refs[i])); n++; });
console.log(JSON.stringify({n: n, worst: worst}));
"""
try:
    out = subprocess.run(["node", "-e", js, HERE], capture_output=True, text=True, check=True).stdout
    res = json.loads(out)
    report("Browser (stats.js) vs Python", res["worst"] < 2e-5,
           f"{res['n']} numbers compared, largest difference {res['worst']:.1e} (results are stored to 5 decimals)")
except FileNotFoundError:
    print("[SKIP] Browser vs Python: Node.js is not installed")

# 3 ------------------------------------------------------------------------------------
path = os.path.join(HERE, "data", "derived", "results.json")
before = json.load(open(path))
subprocess.run([sys.executable, os.path.join(HERE, "scripts", "analyze.py")], capture_output=True, check=True)
after = json.load(open(path))
before.pop("generated", None)
after.pop("generated", None)
report("Fresh run vs committed results", before == after, "identical" if before == after else "results changed")

sys.exit(0 if ok else 1)
