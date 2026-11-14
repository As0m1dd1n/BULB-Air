# BULB-Air

**Is NO₂ over your city really rising?** BULB-Air tests NASA satellite data season by season and says so when the data cannot answer.

Built for the NASA Space Apps Challenge 2026, challenge *Be An Earth System Trend Detective!*

Most trend tools draw one line through a whole year and report one number. For a city like Tashkent that hides the main question: NO₂ is highest in winter, and winter is when the satellite sees the city least. BULB-Air gives each season its own verdict, shows how many days the satellite actually saw, and lets you stop the record at any year to see what the same test would have said then.

## What we found (Tashkent, OMI NO₂, October 2004 to March 2026)

| Season | Trend per decade | 95% range | Usable days | With the record cut at 2020 | Verdict |
|---|---|---|---|---|---|
| Winter (Dec–Feb) | +22% | +10% to +36% | 35% | not proven (−15% to +25%) | **RISING**, one source so far |
| Spring (Mar–May) | +18% | +9% to +26% | 50% | not proven (−4% to +21%) | **RISING** |
| Summer (Jun–Aug) | +23% | +18% to +30% | 71% | rising | **RISING** |
| Autumn (Sep–Nov) | +22% | +15% to +29% | 51% | rising | **RISING** |

Percent of the season's average NO₂ column per decade. Winter NO₂ is about twice the summer level, and the five highest winters of the record are all between 2021 and 2026.

Almaty and Bishkek, tested the same way, also give the other verdicts: Almaty's autumn is NOT PROVEN YET and its winter is SOURCES DISAGREE. All numbers are on the site and in `data/derived/results.json`.

- **RISING / FALLING**: our test is significant and a published study finds the same direction.
- **One source so far**: our longer record shows a trend that neither source finds in the study's own years (it ends in 2021).
- **SOURCES DISAGREE**: on the same years, one finds a clear trend and the other does not.
- **NOT PROVEN YET**: neither finds a clear trend. We then report the smallest trend the record would probably detect. Not proven does not mean the air is clean.

## Run it yourself

```bash
pip install -r requirements.txt
python scripts/fetch_omi.py     # optional, about 6 minutes, no login: re-downloads the AWS part
python scripts/analyze.py       # writes data/derived/ and docs/results.js
python scripts/verify.py        # three checks (needs pymannkendall and Node.js for two of them)
```

Then open `docs/index.html` in a browser. All raw data is already in `data/raw/`, so `analyze.py` runs on its own.

To add a city, add its name and coordinates to `CITIES` in `scripts/fetch_omi.py`, run it, and follow `GIOVANNI.md` for the years after May 2020.

## What is in this repository

| Path | What it is |
|---|---|
| `scripts/fetch_omi.py` | Downloads daily OMI NO₂ cut-outs from NASA's public copy on AWS (to May 2020) |
| `scripts/trendstats.py` | Sen slope, Mann–Kendall with Hamed–Rao correction, confidence interval, detectable trend, false-discovery adjustment |
| `scripts/analyze.py` | Joins the two data parts, builds season values, coverage, verdicts and the comparison with the published study |
| `scripts/verify.py` | Checks the statistics against `pymannkendall`, the browser code against Python, and a fresh run against the stored results |
| `docs/` | The website (static files, works on GitHub Pages). `stats.js` repeats the same test in the browser |
| `data/raw/omi_daily_cutouts.npz` | AWS part: 5,722 days × 3 cities × 6 × 6 grid cells |
| `data/raw/MANIFEST.csv` | Every AWS file used: name, size, MD5, URL |
| `data/raw/giovanni_cells.csv` | Giovanni part: daily values of the 12 grid cells, January 2020 to March 2026 |
| `data/derived/` | Daily and seasonal series per city (CSV) and all results (JSON) |
| `METHOD.md` | The rules, and every change made after the first results |
| `GIOVANNI.md` | Exactly what was requested from Giovanni and how the two parts were checked against each other |
| `REFERENCES.md` | Data and literature citations |
| `PROJECT_PAGE.md` | Text of the Space Apps project page, including the Use of AI statement |
| `LICENSE` | MIT for the code; NASA data is public domain |

## Data

- **NASA**: OMI/Aura NO₂ Cloud-Screened Total and Tropospheric Column, Level 3, daily, 0.25° × 0.25° (OMNO2d, version 003), field `ColumnAmountNO2TropCloudScreened`. NASA GES DISC, doi:10.5067/Aura/OMI/DATA3007. October 2004 to May 2020 from NASA's copy in the Registry of Open Data on AWS; June 2020 to March 2026 from NASA Giovanni.
- **Published comparison**: Sharma et al. (2023), merged OMI (2004–2014) and GOME-2B (2013–2021) seasonal NO₂ trends for 20 cities, doi:10.1039/d2ea00075j, supplementary Table S2.

## Limits

- NO₂ is one pollutant. Tashkent's worst winter pollutant is fine particles (PM2.5), which this record does not measure.
- The satellite measures the whole air column in the early afternoon, not the air at street level.
- It reads only on fairly clear days. Whether clear winter days are cleaner or dirtier than cloudy ones is not tested here.
- Usable days became fewer over the record in every season. Comparing each day with its own month limits the effect on the trend but cannot remove it.
- The published study shares the OMI sensor until 2014 and ends in 2021. Where both are clear on the same years, its trends are 1.1 to 3.5 times ours.
- The winter rise for Tashkent rests on one source so far.

## Credits

Team RareFlow Aleshi, Tashkent. NASA does not endorse this project. Use of AI is described in `PROJECT_PAGE.md`.
