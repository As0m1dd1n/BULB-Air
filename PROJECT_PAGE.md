# Space Apps project page: text to paste

Challenge: **Be An Earth System Trend Detective!**

## Project Name

BULB-Air

## High-Level Project Summary

BULB-Air is a free website that checks whether nitrogen dioxide (NO₂) pollution, measured from space by NASA's OMI instrument, is really increasing over each of the 14 regions of Uzbekistan, separately for each season. It is for students, journalists and city groups who need a number they can trust. Most trend tools give one slope for the whole year; ours also says how many days the satellite actually saw and when the data cannot answer. We tested 21 years of NASA's daily OMNO2d product (October 2004 to March 2026). Over Tashkent, NO₂ rose by about 20% per decade in all four seasons by our test; a published study confirms the direction for summer and autumn. Winter is when NO₂ is highest and when the satellite has the fewest usable readings (35% of days), so the winter rise is marked unconfirmed. Every region rose faster than empty desert in at least one season, most in the Fergana Valley, Tashkent, Samarkand and Jizzakh. Anyone can drop in a NASA Giovanni CSV and run the same test for another place or variable.

## Link to Project Demo

(public link to the 7-slide deck)

## Link to Final Project

(public link to the GitHub repository; the live site is its GitHub Pages address)

## Detailed Project Description

**What it does.** BULB-Air opens on four verdicts for Tashkent, one per season, with no clicks. Each card shows the trend in percent per decade, its 95% range and the share of days with a usable satellite reading. Selecting a season shows the evidence: the yearly values, the trend line, the p-value, the smallest trend likely to be detected and a check with other box sizes. A slider stops the record at any earlier year and reruns the test in the browser. A calendar shows every day of the record as seen or not seen. A table compares our result with a published study. The verdicts are:

- RISING or FALLING: our test is clear and the second source finds the same direction.
- One source so far: our longer record shows a trend that neither source finds in the study's own years.
- SOURCES DISAGREE: on the same years, one finds a clear trend and the other does not.
- NOT PROVEN YET: neither finds a clear trend. The site then states the smallest trend the record would probably detect, so that "not proven" is never read as "the air is clean".

**How it answers the challenge.**

1. *Identify variables.* We chose one variable with a long NASA record and a clear local question, tropospheric NO₂. Any other Giovanni variable can be tested through the CSV upload, with a sample file to try first.
2. *Acquire data for a region.* A script reads only the grid cells around each city from NASA's public OMNO2d files, with no login; the years after May 2020 come from NASA Earthdata Cloud OPeNDAP (free Earthdata login), checked against NASA Giovanni for Tashkent. A city is added with one line.
3. *Time series and visualization.* Yearly values per season with the trend line, a monthly chart of usable days, and a day-by-day calendar of what the satellite saw.
4. *Statistical analysis.* Sen slope, Mann–Kendall test with the Hamed–Rao correction for autocorrelation, 95% confidence interval, Benjamini–Hochberg adjustment across all 56 region-season tests, and the smallest trend likely to be detected (after Weatherhead et al.). The seasonal cycle is removed by testing each season separately and comparing each day with its own month, as the challenge suggests.

**What we found.** Tashkent, 0.5° box, 2005 to 2026:

- Winter: +22% per decade (range +10% to +36%), usable data on 35% of days. Rising, unconfirmed: one source so far.
- Spring: +18% (+9% to +26%). Sources disagree: on the study's years 2005–2021 the study finds a clear rise and our test does not.
- Summer: +23% (+18% to +30%). Rising; the published study finds the same direction, at 3.5 times our rate on the same years.
- Autumn: +22% (+15% to +29%). Rising; same direction, 2.2 times our rate on the same years.

With the record stopped at 2020, winter and spring are both not proven. The five highest winters of the record all fall between 2021 and 2026. Across all 14 regions of Uzbekistan (2004 to 2026) NO₂ rose everywhere, and less over empty desert, so we flag a region 🚩 where NO₂ rose clearly faster than the desert background. Every region is flagged in at least one season; 8 in all four (Tashkent, Almalyk (Tashkent region), Andijan, Fergana, Jizzakh, Namangan, Samarkand, Gulistan), Navoi and Nukus in one. Our own test for Tashkent gives the same verdict with a single grid cell and with boxes of 1° and 1.5°.

**Why it matters.** The usual tool gives one slope and one p-value and leaves a student or a journalist to over-read it. BULB-Air teaches the opposite habit with a real local case: ask how much was observed, what size of change could have been detected, whether a second source agrees, and what the same test would have said five years ago.

**Who it is for.** High-school and university students learning to read data; journalists and city groups who need a statement they can quote together with its limits.

**Limits.** NO₂ is one pollutant; Tashkent's worst winter pollutant is PM2.5, which this record does not measure. The satellite measures the whole air column once a day in the early afternoon, on fairly clear days only, and usable days became fewer over the years. The second source shares the OMI sensor until 2014 and ends in 2021; where both are clear on the same years its trends are 2.2 to 3.5 times ours, so we claim agreement on direction only. The winter rise for Tashkent rests on one source so far and depends on the years after we join two copies of the NASA record in 2020. In its last years Aura's overpass drifted later in the afternoon; we have not corrected for this. Every verdict is about the NO₂ column, not street-level air and not PM2.5.

**Next steps.** Add TROPOMI as a fully independent second satellite; test with ground PM2.5 data whether the clear winter days the satellite sees are cleaner than the days it misses; add a chooser of ready-made Giovanni variables.

**Tools.** Python (NumPy, Rasterio, Requests) for the data and statistics; plain HTML, CSS and JavaScript for the site (no framework); NASA Earthdata Cloud OPeNDAP for the recent years, checked against NASA Giovanni; GitHub Pages for hosting.

## NASA Data

- **OMI/Aura NO₂ Cloud-Screened Total and Tropospheric Column, Level 3, daily, 0.25° × 0.25° (OMNO2d, version 003)**, field `ColumnAmountNO2TropCloudScreened`. NASA GES DISC, doi:10.5067/Aura/OMI/DATA3007. Every number on the site is computed from it.
  - 1 October 2004 to 31 May 2020: all 5,688 daily files in NASA's copy in the Registry of Open Data on AWS (https://registry.opendata.aws/omi-no2-nasa/). File list with checksums: `data/raw/MANIFEST.csv`.
  - 1 June 2020 to 15 March 2026: the same product through **NASA Earthdata Cloud OPeNDAP** (https://opendap.earthdata.nasa.gov/, collection C1266136111-GES_DISC), one window over Uzbekistan per day. For Tashkent also through **NASA Giovanni** (https://giovanni.gsfc.nasa.gov/giovanni/), one grid cell at a time, as a check: the two agree on all 4,192 cell-days. Settings: `GIOVANNI.md`.
- **NASA Giovanni** is also the route for users: the site accepts its time-series CSV files, so the same test can be run on any Giovanni variable and region.

## Space Agency Partner & Other Data

- Sharma, B. R., Kuttippurath, J., Gopikrishnan, G. S. and Pathak, M. (2023), *Environmental Science: Atmospheres* 3, 905–918, doi:10.1039/d2ea00075j, supplementary Table S2. Seasonal NO₂ trends from merged OMI and GOME-2B data; GOME-2B flies on EUMETSAT's Metop-B satellite. Used as the second source.
- World Bank (2024), *Air Quality Assessment for Tashkent and the Roadmap for Air Quality Management Improvement in Uzbekistan*. Used for the PM2.5 context.
- Statistical methods: Mann (1945), Kendall (1975), Sen (1968), Hamed and Rao (1998), Gilbert (1987), Weatherhead et al. (1998), Benjamini and Hochberg (1995). Full list in `REFERENCES.md`.
- Fonts: Bricolage Grotesque, IBM Plex Sans, IBM Plex Mono, Space Grotesk and Inter (SIL Open Font License, Google Fonts).

## Use of Artificial Intelligence

We used **Claude (Anthropic)** throughout the project, in two products: the claude.ai app (chat, and browser control to operate NASA Giovanni and Earthdata in our signed-in browser) and **Claude Code** (an agent that edits and runs code in the repository; most commits in the history are authored by it). Models: Claude Opus and Claude Sonnet.

- **Code.** Claude wrote the data download script, the statistics, the analysis script and the website code under our direction, and operated NASA Giovanni and Earthdata Cloud OPeNDAP in our browser, signed in to our Earthdata account, to request the recent years. The statistics are checked against the independent `pymannkendall` package and the browser version against the Python version (`scripts/verify.py`).
- **Text and slides.** Claude drafted the project description, the README, the method document, and the text, layout and code-drawn charts of the slides, including the line graphic on the title slide. We reviewed and edited them.
- **Review.** Before and during the hackathon we used Claude to simulate a panel of judges on our pitch and project to find weak points. No project code or data analysis was produced before the hackathon started.
- **No AI-generated images, video or audio** are used. All charts are drawn by code from the NASA data. No NASA logos or branding are used.

The team chose the challenge, the city and the question, decided what the tool should show, and is responsible for the result.
