# TODO — fixes from jury run v4 (17 agents)

Scores v4 (mean): Influence 5.4 · Creativity 7.1 · Validity 6.9 · Relevance 6.75 · Presentation 5.0 · idea potential 7.4.
Votes: 0 ADVANCE, 13 BORDERLINE, 3 NO. All NOs came from private links. Judge 6: ADVANCE if links are public and item 6 is solved.
Best-fit award: Best Use of Science.

Rule for every item: change code/text, rerun `python scripts/analyze.py` and `python scripts/verify.py`, update every number in README, docs, PROJECT_PAGE and pitch/ from `data/derived/results.json`, log method changes in METHOD.md section 8, then commit.

## Owner: user (not Claude Code)
1. Push repo to GitHub, enable Pages from `/docs`, make the deck public, open both links in an incognito window, add team member names (cover slide + project page), read "Use of AI" in PROJECT_PAGE.md and correct it to what the team really did. Without this: Presentation 4 and NO votes.
13. No real users (Influence 5): if possible, show it to one journalist or city specialist and quote one line.

## Claude Code, no new data needed (priority order)
2. Winter rests on the joined Giovanni years 2021–2026. Mark Tashkent winter "RISING, unconfirmed"; add to Limits: Aura overpass-time drift, usable winter days fell 38 → 27, winter +22% equals the 22% detectable trend. Add a control on a nearby clean box if the data allows.
3. "Published study agrees" is too strong: only the sign matches; on the same years it is 2–5x larger. Spring: ours not clear (+0.054), theirs clear (+0.29) = SOURCES DISAGREE by our own rule, but the card says RISING. Reword to "same direction, size differs 2–3.5x" and fix the verdict logic if needed.
4. Remove the claim "rules were written before the analysis" (docs/index.html line ~240 and anywhere else). METHOD.md items 2 and 7 were written after results; item 7 moved winter from DISAGREE to RISING.
5. Multiple comparisons: Benjamini–Hochberg is applied to 4 seasons only; there are 12 city-season pairs plus box variants and the slider. Apply BH over 12, show raw and adjusted p, label the slider "exploratory". Almaty summer adjusted p ~0.07 is marked "clear".
6. The "2x published ±" rule must hold under both readings of ±: show the verdict under both. Almaty autumn and winter are on the edge.
7. Box check contradicts its caption: winter to 2020 is not proven at 0.5° and 1.0° but rising at 1.5°; larger boxes stop at 2020. Fix the caption or the check.
8. Month climatology is computed from the whole record (possible leakage in the slider test for end year 2020). Compute it only from years up to the chosen end year.
10. Day counts 7,834 vs 7,836: make consistent. Slide 6 "before 2020" numbers (summer +26%, autumn +17%) do not match METHOD (+29–30%, +19%): align with results.json.
11. NO₂ ≠ PM2.5: label verdicts "NO₂ column: RISING" and add the ready sentence "column NO₂, not street level, not PM2.5". State that there is no link to a ground monitor.
15. Slides 2, 3, 5 are overloaded. Add a calendar screenshot, a note "chart drawn by code, with help from Claude", and put the winter 2020 → 2026 change on the front.

## Claude Code, needs a script
9. Not repeatable: the 12 Giovanni cells were collected by hand. Commit the 12 original CSVs with headers, a script that joins them into `data/raw/giovanni_cells.csv`, and a CI check that runs `analyze.py` + `verify.py`.

## Scope change (decided 14 Nov): Uzbekistan only
16. Replace Almaty and Bishkek with Uzbek cities. Candidates: Samarkand, Fergana, Navoi, Almalyk/Angren industrial zone (final list: team).
   a. `scripts/fetch_omi.py`: change `CITIES`, rerun (AWS copy, no login, 2004-10 … 2020-05).
   b. 2020-06 … 2026-03: write `scripts/fetch_giovanni.py` (or GES DISC OPeNDAP via `earthaccess`) using the user's Earthdata login from `~/.netrc` (never committed); same 4 cells per city; reproduce the Tashkent part of `giovanni_cells.csv` first as a check (this also closes item 9).
   c. Add a rural control box near each city (no big NO₂ sources) and show it next to the city verdict.
   d. `PUBLISHED`: keep only cities that are actually in Sharma et al. Table S2 (check the table; Tashkent is). Others get "one source only" and the site says so.
   e. Remove Almaty/Bishkek from site tabs, README, PROJECT_PAGE, slides; log the change in METHOD.md section 8 with the reason.
   f. Run analyze.py + verify.py; update all numbers.
   Do this AFTER items 1–8: links and honest wording come first.

## Later (not before the deadline)
12. Variable choice (challenge goal 1) is weak: one variable plus manual Giovanni. A second satellite (TROPOMI) and ground PM2.5 are next steps.

## Leave alone
The NOT PROVEN YET verdict and the season-by-season design: judges praised them unanimously.
