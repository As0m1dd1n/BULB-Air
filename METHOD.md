# Method

The rules in sections 1 to 5 were written on 14 November 2026 before the analysis was first run. Every change made after the first results is listed in section 8, with what it did to the numbers.

## 1. Data

- Product: OMI/Aura OMNO2d v003, daily, 0.25° × 0.25°, field `ColumnAmountNO2TropCloudScreened` (tropospheric NO₂ column from pixels with cloud fraction below 30%). Unit: molecules per cm²; we report 10¹⁵ molecules per cm².
- 1 October 2004 to 31 May 2020: every daily file in the public AWS copy (5,688 files; 34 days have no file).
- 1 June 2020 to 15 March 2026: the same product through NASA Earthdata Cloud OPeNDAP (collection C1266136111-GES_DISC; every daily granule listed by NASA CMR, 2,112 days), one window over Uzbekistan per day (`scripts/fetch_opendap_browser.js`, `scripts/import_opendap.py`). Earlier, the Tashkent cells were read through NASA Giovanni one cell at a time (see `GIOVANNI.md`); this is now an independent check: on all 4,192 Tashkent cell-days both copies agree (correlation 0.99999999, mean ratio 1.000).
- Fill values (−1.2676506 × 10³⁰) are treated as missing.

## 2. City box and usable days

- All 14 regions of Uzbekistan, one box per regional centre. Tashkent region is represented by Almalyk (an industrial town), because the box over its centre Nurafshon would overlap the Tashkent city box. No two boxes share a cell.
- The box is the 2 × 2 grid cells (0.5° × 0.5°) that meet at the grid corner nearest to the centre. Tashkent (Tashkent city): 41.00–41.50° N, 69.00–69.50° E; Almalyk (Tashkent region): 40.50–41.00° N, 69.25–69.75° E; Andijan (Andijan region): 40.50–41.00° N, 72.00–72.50° E; Bukhara (Bukhara region): 39.50–40.00° N, 64.25–64.75° E; Fergana (Fergana region): 40.25–40.75° N, 71.50–72.00° E; Jizzakh (Jizzakh region): 39.75–40.25° N, 67.50–68.00° E; Namangan (Namangan region): 40.75–41.25° N, 71.50–72.00° E; Navoi (Navoi region): 39.75–40.25° N, 65.25–65.75° E; Karshi (Kashkadarya region): 38.50–39.00° N, 65.50–66.00° E; Samarkand (Samarkand region): 39.50–40.00° N, 66.75–67.25° E; Gulistan (Syrdarya region): 40.25–40.75° N, 68.50–69.00° E; Termez (Surkhandarya region): 37.00–37.50° N, 67.00–67.50° E; Urgench (Khorezm region): 41.25–41.75° N, 60.50–61.00° E; Nukus (Republic of Karakalpakstan): 42.25–42.75° N, 59.25–59.75° E.
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
- Family: all region-season tests shown as verdicts (56: 14 regions × 4 seasons) are one family. The tests on the published study's years form a second family (Tashkent only, 4 tests). We adjust their p-values together with the Benjamini–Hochberg procedure, which controls the expected share of false discoveries, and compare the adjusted value with 0.05. The site shows the adjusted p-value.
- Our own test says RISING or FALLING when the adjusted p is below 0.05, NOT PROVEN YET otherwise, and TOO LITTLE DATA with fewer than 10 season values.

## 5. Smallest trend likely to be detected

Following Weatherhead et al. (1998), a trend is detected with 90% probability at the 5% level when it exceeds about 3.3 standard errors (1.96 for the level plus 1.28 for the power). We take the standard error from the 95% interval of the Sen slope:

    detectable trend = 3.3 × (upper − lower) / (2 × 1.96)

so the interval and this threshold rest on the same estimate of the noise. A real change smaller than this would probably be missed. It can still be detected, with less than 90% probability.

## 6. Second source and verdict

- Second source: Sharma et al. (2023), supplementary Table S2, seasonal NO₂ trends from merged OMI (2004–2014) and GOME-2B (2013–2021), November 2004 to March 2021, in 10¹⁵ molecules per cm² per year.
- The paper does not say whether its ± is one standard error or a 95% range. The verdict uses the strict reading: a published trend is clear when |trend| ≥ 2 × its ±. The site also shows the verdict under the lenient reading (|trend| ≥ ±) wherever it differs; in the current results this happens for Almaty autumn only.
- Agreement means the same direction only. The published trends are 1.1 to about 5 times ours on the same years; the paper does not state the area it averaged over.
- Verdict. We first compare like with like: our own test on the study's years (2005–2021) against the published trend.
  - RISING / FALLING: on the study's years both are clear with the same sign, and our full-record test agrees.
  - SOURCES DISAGREE: on the study's years one is clear and the other is not, or both are clear with opposite signs.
  - RISING / FALLING, one source so far (shown as "unconfirmed"): neither is clear on the study's years, but our full-record test is. The trend shows only in years the study does not cover.
  - NOT PROVEN YET: none of the three is clear.
- With no second source (another city, an uploaded file) the verdict is our own test, marked "one source only".
- The second source shares the OMI sensor for 2004–2014, so it is only partly independent.

## 6a. Desert background and the red flag

- NO₂ also rises over open desert, so part of every region's rise is regional background or slow drift of the instrument. Three background boxes of the same size, with no town or plant inside: Kyzylkum W: centre 41.50° N, 62.00° E; Kyzylkum E: centre 42.50° N, 65.00° E; Ustyurt: centre 44.00° N, 57.00° E.
- Background season value = mean of the three boxes' season values (same anomaly method), where at least two boxes have a value.
- Excess series = region's season value minus the background value of the same season and year. It is tested like any series (section 4); the 56 excess tests form their own Benjamini–Hochberg family.
- Red flag: at least one season whose excess rises clearly (adjusted p < 0.05). The site also shows in how many of the four seasons.
- Limit: subtracting the background removes a drift that adds the same amount everywhere. A drift that scales with the level (a percentage error) would still leave some excess in polluted regions. The background boxes are 100–700 km from some regions (Termez, the Fergana valley).

## 7. Checks

Run `python scripts/verify.py`.

- `scripts/trendstats.py` against the `pymannkendall` package on 300 random autocorrelated series: identical slopes; p-values within 0.002, except where our stricter correction rule applies.
- `docs/stats.js` against the Python results for all 56 region-season series: differences below 10⁻⁵.
- A fresh run of `analyze.py` reproduces the stored `results.json`.
- Join of the two data parts: see `GIOVANNI.md`.
- Box size: our own test is repeated for the single cell that contains the city centre (full record) and for 4 × 4 and 6 × 6 cells, all on the full record.
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
8. **Like-with-like comparison (jury review, 14 Nov).** The earlier rule compared the published trend with our full record (to 2026) in one case and with our test on the study's years in another. For Tashkent spring this called two sources "agreeing" although on the shared years 2005–2021 our test was not clear (+0.054 per year, p = 0.06) and the study's was (+0.29 ± 0.04). The rule now always compares on the shared years first (section 6). Effect: Tashkent spring changes from RISING to SOURCES DISAGREE; no other verdict changes in any city. This change was made after the results were known; it makes the verdicts stricter, not more favourable.
9. **One family across cities (jury review, 14 Nov).** The Benjamini–Hochberg adjustment covered the four seasons of one city; it now covers all 12 city-season tests together, for the full record and for the study's period. Box-size checks, the record cut at 2020 and the year slider keep the four-season adjustment and are labelled exploratory. Effect: adjusted p-values moved by small amounts in both directions (Tashkent winter 0.003 to 0.006, Almaty summer 0.047 to 0.028, because Benjamini–Hochberg depends on where a test ranks in the family); no verdict changed.
10. **Both readings of the published ±.** The strict reading stays the rule; the lenient reading is now shown where it gives another verdict (Almaty autumn: NOT PROVEN YET under the strict reading, SOURCES DISAGREE under the lenient one).
11. **Monthly normal levels from the tested years only.** When a test uses only part of the record (the study's years, the record cut at 2020), the normal level of each month is now computed from those years only, so later years cannot leak into an earlier test. The browser slider still uses the full-record normal levels and is labelled exploratory. Effect: small changes in the period-limited slopes (Tashkent spring 2005–2021: +0.054 to +0.052 per year); no verdict changed.
12. **Box-size check compared like with like.** The wider boxes exist only to 2020, so the site now sets them against our own box cut at 2020, and states whether the verdict depends on the box size. For Tashkent winter and spring it does.
13. **All 14 regions of Uzbekistan instead of Almaty and Bishkek (team decision, 14 Nov).** The project is about Uzbekistan; we include every region rather than choosing some. New boxes were fetched from the same AWS copy (2004-10 to 2020-05); the Tashkent cut-outs reproduced bit for bit. The Giovanni extension to 2026 exists for Tashkent only, so the other regions end in May 2020. Only Tashkent has a published second source; the other regions are "one source only". With 56 tests in the family instead of 12, Tashkent's adjusted p-values changed slightly; no Tashkent verdict changed.
14. **Desert background and red flag (section 6a), added after the 14-region results were known.** First rule tried: flag every region with a rising season. It flagged all 14, because NO₂ rose everywhere, including the desert (winter +14% (p = 0.096), spring +9% (p = 0.065), summer +17% (p = 0.002), autumn +16% (p = 0.018) per decade). That rule could not tell regions apart, so the flag now uses the excess over the desert. Effect: 13 of 14 regions flagged; seasons with a clear excess: Andijan 4, Fergana 4, Namangan 4, Karshi 4, Gulistan 4, Samarkand 3, Tashkent 2, Almalyk 2, Bukhara 2, Jizzakh 2, Termez 2, Urgench 1, Nukus 1, Navoi 0.
15. **All regions extended to March 2026 (14 Nov).** The 13 new regions and the desert boxes were extended with NASA Earthdata Cloud OPeNDAP (section 1), so every region now has the same period, October 2004 to March 2026, and the wider boxes for Tashkent run to 2026 as well. Effects: the desert background rise became smaller (winter +10% (p = 0.055), spring +1%, summer +4%, autumn +9% (p = 0.006) per decade). Under the fixed red-flag rule all 14 regions are now flagged; clear excess in 4 of 4 seasons: Tashkent, Almalyk (Tashkent region), Andijan, Fergana, Jizzakh, Namangan, Samarkand, Gulistan; 3: Bukhara, Karshi, Urgench; 2: Termez; 1: Navoi, Nukus. Navoi winter and Nukus spring were the only remaining NOT PROVEN YET cases in item 14 and changed. Tashkent's verdicts did not change. With the full record, Tashkent winter and spring rise at every box size (item 12 no longer applies). We did not change the flag rule after seeing these results; the number of flagged seasons is what separates the regions.
