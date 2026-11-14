/* BULB-Air: OMNO2d v003 for June 2020 - March 2026 from NASA Earthdata Cloud OPeNDAP.
   This is the exact code used on 14 Nov 2026 to make data/raw/opendap_2020_2026.txt.

   How to run
   1. Sign in at https://urs.earthdata.nasa.gov (free account) in Chrome.
   2. Open any OMNO2d granule page on https://opendap.earthdata.nasa.gov/ (so requests are same-origin
      and carry the Earthdata session), e.g.
      https://opendap.earthdata.nasa.gov/collections/C1266136111-GES_DISC/granules/OMNO2d.003%3AOMI-Aura_L3-OMNO2d_2020m0601_v003-2020m0825t144124.he5.dmr.html
   3. Paste this file into the DevTools console. Progress: window.__job.done / 2112.
   4. When window.__job.status is "finished", run saveJob() to download opendap_2020_2026.txt,
      put it in data/raw/, then: python scripts/import_opendap.py && python scripts/analyze.py

   Window: rows 500-543 (cell centres 35.125-45.875 N; row 0 is the southernmost), columns 940-1015
   (55.125-73.875 E). Output: one line per day "YYYY-MM-DD<TAB>row;row;..." rows south to north. */
window.__job = { done: 0, err: [], data: {}, list: null, status: "listing" };
(async () => {
  const J = window.__job;
  try {
    let list = [], after = null;
    while (true) {
      const h = after ? { "CMR-Search-After": after } : {};
      const r = await fetch("https://cmr.earthdata.nasa.gov/search/granules.json?short_name=OMNO2d&version=003&temporal=2020-06-01T00:00:00Z,2026-03-15T23:59:59Z&page_size=2000&sort_key=start_date", { headers: h });
      after = r.headers.get("CMR-Search-After");
      const es = (await r.json()).feed.entry;
      es.forEach(e => list.push([e.time_start.slice(0, 10), e.title]));
      if (es.length < 2000 || !after) break;
    }
    J.list = list; J.status = "fetching";
    const R0 = 500, R1 = 543, C0 = 940, C1 = 1015;
    const ce = encodeURIComponent("/HDFEOS/GRIDS/ColumnAmountNO2/Data_Fields/ColumnAmountNO2TropCloudScreened[" + R0 + ":1:" + R1 + "][" + C0 + ":1:" + C1 + "]");
    let i = 0;
    async function worker() {
      while (i < list.length) {
        const [d, title] = list[i++];
        for (let a = 0; a < 4; a++) {
          try {
            const u = "https://opendap.earthdata.nasa.gov/collections/C1266136111-GES_DISC/granules/" + encodeURIComponent(title) + ".dap.csv?dap4.ce=" + ce;
            const r = await fetch(u, { credentials: "include" });
            if (!r.ok) throw new Error("HTTP " + r.status);
            const tx = await r.text();
            const rows = tx.split("\n").filter(l => l.indexOf("[") >= 0 && l.indexOf(",") > 0).map(l => l.slice(l.indexOf(",") + 1).trim());
            if (rows.length !== R1 - R0 + 1) throw new Error("rows " + rows.length);
            J.data[d] = rows.join(";");
            break;
          } catch (e) { if (a === 3) J.err.push([d, String(e)]); else await new Promise(s => setTimeout(s, 2000 * (a + 1))); }
        }
        J.done++;
      }
    }
    await Promise.all(Array.from({ length: 8 }, worker));
    J.status = "finished";
  } catch (e) { J.status = "failed: " + e; }
})();
function saveJob() {
  const J = window.__job;
  const txt = Object.keys(J.data).sort().map(d => d + "\t" + J.data[d]).join("\n") + "\n";
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([txt], { type: "text/plain" }));
  a.download = "opendap_2020_2026.txt"; document.body.appendChild(a); a.click();
}
