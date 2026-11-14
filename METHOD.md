# Method

The rules in sections 1 to 5 were written on 14 November 2026 before the analysis was first run. Every change made after the first results is listed in section 8, with what it did to the numbers.

## 1. Data

- Product: OMI/Aura OMNO2d v003, daily, 0.25° × 0.25°, field `ColumnAmountNO2TropCloudScreened` (tropospheric NO₂ column from pixels with cloud fraction below 30%). Unit: molecules per cm²; we report 10¹⁵ molecules per cm².
- 1 October 2004 to 31 May 2020: every daily file in the public AWS copy (5,688 files; 34 days have no file).
- 1 June 2020 to 15 March 2026: the same product through NASA Giovanni, one grid cell at a time (see `GIOVANNI.md`).
- Fill values (−1.2676506 × 10³⁰) are treated as missing.

## 2. City box and usable days

- The box is the 2 × 2 grid cells (0.5° × 0.5°) that meet at the grid corner nearest to the city centre. Tashkent: 41.0–41.5° N, 69.0–69.5° E. Almaty: 43.0–43.5° N, 76.75–77.25° E. Bishkek: 42.5–43.0° N, 74.25–74.75° E.
- A day is usable when at least 2 of the 4 cells have a value. The daily value is the mean of the valid cells.
- Coverage of a season = usable days ÷ days in the season.

## 3. Seasons

- DJF, MAM, JJA, SON. December belongs to the winter of the following year.
- A season of a year is used when it is complete in the record (at least 85 days) and has at least 10 usable days.
- Season value: each usable day is compared with the long-term mean of its calendar month. The season value is the season's normal level (the mean of its three monthly means) plus the average of these daily differences. This keeps a change in which days were seen from looking like a change in the air.
- This gives 21 or 22 values per season (2005 to 2025, winter to 2026).

## 4. Trend and test

- Trend: Sen slope (median of all pairwise slopes), in 10¹⁵ molecules per cm² per year. We also give it as percent of the season's mean level per decade.
- Test: Mann–Kendall, two-sided, 5% level, with the Hamed and Rao (1998) variance correction for autocorrelation (only lags whose rank autocorrelation is significant at 5% enter the correction, and the correction may only make the test stricter).
- Interval: 95% confidence interval of the Sen slope (Gilbert 1987), using the corrected variance. The interval is not adjusted for the number of seasons.
- Family: the four seasons of one city are one family of tests. We adjust the four p-values with the Benjamini–Hochberg procedure, which controls the expected share of false discoveries, and compare the adjusted value with 0.05. The site shows the adjusted p-value.
- Our own test says RISING or FALLING when the adjusted p is below 0.05, NOT PROVEN YET otherwise, and TOO LITTLE DATA with fewer than 10 season values.

## 5. Smallest trend likely to be detected

Following Weatherhead et al. (1998), a trend is detected with 90% probability at the 5% level when it exceeds about 3.3 standard errors (1.96 for the level plus 1.28 for the power). We take the standard error from the 95% interval of the Sen slope:

    detectable trend = 3.3 × (upper − lower) / (2 × 1.96)

so the interval and this threshold rest on the same estimate of the noise. A real change smaller than this would probably be missed. It can still be detected, with less than 90% probability.

## 6. Second source and verdict

- Second source: Sharma et al. (2023), supplementary Table S2, seasonal NO₂ trends from merged OMI (2004–2014) and GOME-2B (2013–2021), November 2004 to March 2021, in 10¹⁵ molecules per cm² per year.
- The paper does not say whether its ± is one or two standard errors. We call a published trend clear when |trend| ≥ 2 × its ±, which holds under either reading.
- We compare direction only. Where both are clear on the same years, the published trends are 1.1 to 3.5 times ours; the paper does not state the area it averaged over.
- Verdict:
  - RISING / FALLING: our full-record test and the published trend are both clear and have the same sign.
  - RISING / FALLING, one source so far: our full-record test is clear, the published trend is not, and our own test on the study's years (2005–2021) is not clear either. The two do not disagree; the trend shows only in years the study does not cover.
  - SOURCES DISAGREE: our test is clear on the study's years and the published trend is not; or the published trend is clear and our full-record test is not; or both are clear with opposite signs.
  - NOT PROVEN YET: neither is clear.
- With no second source (another city, an uploaded file) the verdict is our own test, marked "one source only".
- The second source shares the OMI sensor for 2004–2014, so it is only partly independent.

## 7. Checks

Run `python scripts/verify.py`.

- `scripts/trendstats.py` against the `pymannkendall` package on 300 random autocorrelated series: identical slopes; p-values within 0.002, except where our stricter correction rule applies.
- `docs/stats.js` against the Python results for all 12 city-season series: differences below 10⁻⁵.
- A fresh run of `analyze.py` reproduces the stored `results.json`.
- Join of the two data parts: see `GIOVANNI.md`.
- Box size: our own test is repeated for the single cell that contains the city centre (full record) and for 4 × 4 and 6 × 6 cells (to 2020 only, because the Giovanni part holds the 2 × 2 cells).
- Usable days: the site reports, per season, the number of usable days in the first and last year. They fell in every season and city.

## 8. Change log (after first results)

The first results used the AWS part only (to May 2020).

1. **Stricter correction.** The Hamed–Rao factor is no longer allowed to fall below 1, because with about 20 points an apparent negative autocorrelation is noise and would make the test too lenient. Effect at the time: Almaty summer p rose from below 0.001 to 0.003. No verdict changed.
2. **Rule for the second source.** The rule in section 6 was written after our own test results were known. It uses only the published numbers and a fixed threshold.
3. **Seasons.** The first pitch deck spoke of a cold and a warm season. Before any computation we switched to the four standard seasons so that the results can be compared with the published table.
4. **Month anomalies.** Season values were first plain means of the usable days. A review pointed out that the number of usable days fell over the years and that the mix of days inside a season can shift. We changed to the anomaly method in section 3. Effect on Tashkent to 2020: winter +7% to +8% per decade, spring +8% to +9%, summer unchanged at +29 to +30%, autumn +20% to +19%. No verdict changed in any city.
5. **One noise estimate.** The detectable trend was first computed from the residual scatter (Weatherhead's formula), the interval from the rank-based variance. The two disagreed (winter: 27% against an interval that implied about 33%). We now derive the detectable trend from the interval (section 5). Effect: thresholds changed by a few points; verdicts do not depend on this number.
6. **Record extended to March 2026.** We added June 2020 to March 2026 from NASA Giovanni. Effect on Tashkent: winter changed from NOT PROVEN YET to rising (+22% per decade), spring from SOURCES DISAGREE to RISING; summer and autumn stayed RISING. The site's slider shows the result for any end year.
7. **Trend after the second source ends.** With the longer record, our winter test for Tashkent became clear while the published study (to 2021) is not. Under the earlier rule this would read SOURCES DISAGREE, although on the study's own years our test is not clear either. We added the "one source so far" case in section 6. Effect: Tashkent winter and Almaty spring read RISING, one source so far, instead of SOURCES DISAGREE.
