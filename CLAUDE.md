# BULB-Air — NASA Space Apps 2026

Formerly "BULB-Air": rename every occurrence to **BULB-Air** (site title, README, METHOD, PROJECT_PAGE, deck, footer).
Challenge: *Be An Earth System Trend Detective!* Team: RareFlow Aleshi, Tashkent. Deadline: end of hackathon, 15 Nov 2026.

## What it is
Season-by-season trend test of NASA OMI tropospheric NO₂ over all 14 regions of Uzbekistan (all Oct 2004 – Mar 2026; Tashkent also has a published second source).
Red flag 🚩 = in at least one season NO₂ rose clearly faster than over three desert background boxes (METHOD.md 6a).
Each season gets one verdict, and the tool says so when the data cannot answer:
- RISING / FALLING — our test significant AND second source (Sharma et al. 2023, Table S2) clear, same sign
- SOURCES DISAGREE — one clear, the other not, or opposite signs
- NOT PROVEN YET — neither clear; show the smallest detectable trend ("not proven" ≠ "air is clean")
- TOO LITTLE DATA — fewer than 10 season values
Without a second source (other cities, uploaded CSV) the verdict is our own test, labelled "one source only".

## Layout
- `scripts/fetch_omi.py` — daily OMNO2d v003 cut-outs from NASA's AWS copy (no login, 2004-10 … 2020-05)
- `scripts/fetch_opendap_browser.js` + `scripts/import_opendap.py` — 2020-06 … 2026-03 from Earthdata Cloud OPeNDAP (Earthdata login in the browser)
- `scripts/trendstats.py` — Sen slope, Mann–Kendall + Hamed–Rao (factor never < 1), Gilbert CI, Weatherhead MDT, Benjamini–Hochberg
- `scripts/analyze.py` — seasonal means, coverage, verdicts, robustness (1 cell / 4×4 / 6×6, spring without 2020) → `data/derived/results.json`, `docs/results.js`
- `scripts/verify.py` — checks vs `pymannkendall` and JS vs Python
- `docs/` — static site for GitHub Pages: `index.html`, `stats.js` (mirrors trendstats.py line for line), `results.js`
- `data/raw/` (npz cut-outs + MANIFEST.csv), `data/derived/` (CSV + JSON)
- `METHOD.md` (fixed rules + change log), `REFERENCES.md`, `PROJECT_PAGE.md` (incl. Use of AI), `GIOVANNI.md` (2020-06 … 2026-03 extension)

## Commands
```bash
pip install -r requirements.txt
python scripts/analyze.py      # rerun after any data/method change
python scripts/verify.py       # must pass before every commit that touches stats
python -m http.server -d docs 8000
```

## Hard rules
1. **No invented numbers.** Every number in README, site, deck, PROJECT_PAGE comes from `data/derived/results.json`. After rerunning analysis, update all of them.
2. **Method is fixed.** Any change to the rules in METHOD.md goes into its change log with date, reason and effect on verdicts.
3. `docs/stats.js` and `scripts/trendstats.py` must stay identical in behaviour (verify.py checks it, tolerance 1e-5).
4. Plain English on the site and slides: short sentences, every term explained once, no hype. Limits stated honestly.
5. No NASA logos or branding. No AI-generated images. Charts drawn by code from data.
6. Never commit secrets (Earthdata login, tokens). `.netrc` stays out of the repo.

## Git
- Small commits, one change each, Conventional Commits: `feat:`, `fix:`, `data:`, `docs:`, `refactor:`, `chore:`.
- Run `analyze.py` + `verify.py` before committing anything in `scripts/` or `data/`.
- Push to `main`; GitHub Pages serves `/docs`.
