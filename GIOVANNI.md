# NASA Giovanni: the first route to the years after May 2020, now an independent check

**Status (14 Nov 2026):** the analysis now takes June 2020 to March 2026 from NASA Earthdata Cloud OPeNDAP for every region (`scripts/fetch_opendap_browser.js`, `scripts/import_opendap.py`). The Giovanni cells below were requested first, for Tashkent and for the two cities we later dropped (Almaty, Bishkek; their columns remain in `giovanni_cells.csv` as raw data and are not used). They now serve as a check: on all 4,192 Tashkent cell-days from June 2020 to March 2026, Giovanni and Earthdata Cloud agree (correlation 0.99999999; stored in `results.json` under `extension.check_vs_giovanni`). The text below describes the original request.

The open AWS copy of OMNO2d ends on 31 May 2020. The same product continues at NASA GES DISC, and NASA Giovanni serves it to anyone with a free Earthdata login. On 14 November 2026 it reached 15 March 2026.

## What we requested

| Setting | Value |
|---|---|
| Tool | NASA Giovanni 4.40, https://giovanni.gsfc.nasa.gov/giovanni/ |
| Plot | Time Series, Area-Averaged |
| Variable | NO2 Tropospheric Column (30% Cloud Screened), daily 0.25 deg, `OMNO2d_003_ColumnAmountNO2TropCloudScreened` |
| Dates | 2020-01-01 to 2026-11-13 (data returned to 2026-03-15) |
| Regions | twelve boxes, each holding exactly one 0.25 deg grid cell: the four cells of each city's 2 x 2 box |
| Export | the CSV offered on the result page, one per cell |

The box of a single cell is its centre plus and minus 0.075 degrees. Giovanni reports the cell it used as "Data Bounding Box"; all twelve matched the intended cell centre.

| City | Cell centres (longitude, latitude) |
|---|---|
| Tashkent | 69.125 / 69.375 E, 41.125 / 41.375 N |
| Almaty | 76.875 / 77.125 E, 43.125 / 43.375 N |
| Bishkek | 74.375 / 74.625 E, 42.625 / 42.875 N |

Requesting single cells keeps our rule unchanged: a day is usable when at least two of the four cells have a value. An area-averaged series for the whole box could not apply it.

The twelve CSV files are joined, without any change to the numbers, in `data/raw/giovanni_cells.csv` (one row per day, one column per cell, molecules per cm2, empty = Giovanni fill value).

## How it is joined to the AWS record

(Originally `scripts/analyze.py` used the Giovanni series from 1 June 2020; it now uses Earthdata Cloud OPeNDAP and keeps Giovanni as a check.)

## Checks of the join

1. **Shared months, January to May 2020** (computed by `analyze.py`, checked when Giovanni was the extension; the current check is under `extension.check_vs_giovanni`): 918 cell-days are valid in both sources and none is valid in only one; correlation 0.997; Giovanni is 0.9% higher on average; median absolute difference 0.006 x 10^15 molecules per cm2. The AWS files for 2020 were produced within weeks of the measurement, and NASA has reprocessed those months since.
2. **An older year, 2012** (spot check in the browser, cell 69.125 E, 41.125 N, first 135 days): the same 60 days are valid in both and every value agrees to the rounding used in the check (0.5 x 10^12).

## To repeat it

1. Log in to Giovanni with an Earthdata account.
2. For each cell, choose "Time Series, Area-Averaged", the variable above, the dates, and the bounding box `west,south,east,north` = centre minus/plus 0.075.
3. Plot, open Downloads, save the CSV.
4. Put the twelve value columns side by side under the header used in `data/raw/giovanni_cells.csv`, then run `python scripts/analyze.py`.

A Giovanni CSV can also be dropped straight into the website. The site then treats a day as usable when the file has any value for it.
