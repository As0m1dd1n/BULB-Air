/* BULB-Air trend statistics (browser + Node). Mirrors scripts/trendstats.py line for line.
   Input: one value per year. All rules are fixed in METHOD.md. */
(function (root) {
  "use strict";
  var Z95 = 1.959963984540054;

  function clean(years, values) {
    var p = [];
    for (var i = 0; i < years.length; i++) {
      var t = +years[i], x = values[i];
      if (x !== null && x !== undefined && isFinite(t) && isFinite(x)) p.push([t, +x]);
    }
    p.sort(function (a, b) { return a[0] - b[0]; });
    return { t: p.map(function (q) { return q[0]; }), x: p.map(function (q) { return q[1]; }) };
  }
  function median(a) {
    var s = a.slice().sort(function (p, q) { return p - q; }), n = s.length;
    return n ? (n % 2 ? s[(n - 1) / 2] : 0.5 * (s[n / 2 - 1] + s[n / 2])) : NaN;
  }
  function erfc(x) { // Numerical Recipes erfcc, relative error < 1.2e-7
    var z = Math.abs(x), t = 1 / (1 + 0.5 * z);
    var r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 +
      t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 +
      t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? r : 2 - r;
  }
  function normSf(z) { return 0.5 * erfc(z / Math.SQRT2); }
  function pairwise(t, x) {
    var s = [];
    for (var i = 0; i < t.length; i++) for (var j = i + 1; j < t.length; j++) s.push((x[j] - x[i]) / (t[j] - t[i]));
    return s.sort(function (p, q) { return p - q; });
  }
  function sen(t, x) {
    if (t.length < 3) return { slope: NaN, intercept: NaN };
    var slope = median(pairwise(t, x));
    return { slope: slope, intercept: median(x.map(function (v, i) { return v - slope * t[i]; })) };
  }
  function ranks(a) {
    var idx = a.map(function (v, i) { return i; }).sort(function (p, q) { return a[p] - a[q]; });
    var r = new Array(a.length), i = 0;
    while (i < idx.length) {
      var j = i;
      while (j + 1 < idx.length && a[idx[j + 1]] === a[idx[i]]) j++;
      for (var k = i; k <= j; k++) r[idx[k]] = (i + j) / 2 + 1;
      i = j + 1;
    }
    return r;
  }
  function mannKendall(t, x) {
    var n = x.length;
    if (n < 4) return { n: n, p: NaN, z: NaN, variance: NaN, correction: 1 };
    var S = 0, i, j;
    for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) S += Math.sign(x[j] - x[i]);
    var counts = {}, ties = 0;
    x.forEach(function (v) { counts[v] = (counts[v] || 0) + 1; });
    Object.keys(counts).forEach(function (k) { var c = counts[k]; if (c > 1) ties += c * (c - 1) * (2 * c + 5); });
    var varRaw = (n * (n - 1) * (2 * n + 5) - ties) / 18;
    var slope = sen(t, x).slope;
    var r = ranks(x.map(function (v, k) { return v - slope * (t[k] - t[0]); }));
    var mean = r.reduce(function (a, b) { return a + b; }, 0) / n;
    r = r.map(function (v) { return v - mean; });
    var denom = r.reduce(function (a, b) { return a + b * b; }, 0), corr = 1;
    if (denom > 0) {
      var bound = Z95 / Math.sqrt(n), s = 0;
      for (var k = 1; k < n - 1; k++) {
        var acc = 0;
        for (i = 0; i + k < n; i++) acc += r[i] * r[i + k];
        var rk = acc / denom;
        if (Math.abs(rk) > bound) s += (n - k) * (n - k - 1) * (n - k - 2) * rk;
      }
      corr = 1 + 2 / (n * (n - 1) * (n - 2)) * s;
      if (corr < 1) corr = 1;
    }
    var variance = varRaw * corr;
    var z = S > 0 ? (S - 1) / Math.sqrt(variance) : S < 0 ? (S + 1) / Math.sqrt(variance) : 0;
    return { n: n, S: S, variance: variance, correction: corr, z: z, p: Math.min(1, 2 * normSf(Math.abs(z))) };
  }
  function senCI(t, x, variance) {
    if (t.length < 4 || !isFinite(variance)) return [NaN, NaN];
    var sl = pairwise(t, x), N = sl.length, c = Z95 * Math.sqrt(variance);
    var lo = Math.max(0, Math.min(N - 1, Math.round((N - c) / 2) - 1));
    var hi = Math.max(0, Math.min(N - 1, Math.round((N + c) / 2)));
    return [sl[lo], sl[hi]];
  }
  function minDetectable(t, x) {
    var n = x.length;
    if (n < 5) return { mdt: NaN, noise: NaN, phi: NaN };
    var f = sen(t, x), res = x.map(function (v, i) { return v - (f.intercept + f.slope * t[i]); });
    var m = res.reduce(function (a, b) { return a + b; }, 0) / n;
    res = res.map(function (v) { return v - m; });
    var ss = res.reduce(function (a, b) { return a + b * b; }, 0), sigma = Math.sqrt(ss / (n - 1)), lag = 0;
    for (var i = 0; i + 1 < n; i++) lag += res[i] * res[i + 1];
    var phi = ss > 0 ? lag / ss : 0;
    phi = Math.min(Math.max(phi, 0), 0.8);
    var tm = t.reduce(function (a, b) { return a + b; }, 0) / n;
    var st = t.reduce(function (a, b) { return a + (b - tm) * (b - tm); }, 0);
    return { mdt: 3.3 * sigma / Math.sqrt(st) * Math.sqrt((1 + phi) / (1 - phi)), noise: sigma, phi: phi };
  }
  function benjaminiHochberg(p) {
    var idx = [], out = p.map(function () { return NaN; });
    p.forEach(function (v, i) { if (isFinite(v)) idx.push(i); });
    idx.sort(function (a, b) { return p[a] - p[b]; });
    var m = idx.length, prev = 1;
    for (var k = m - 1; k >= 0; k--) {
      prev = Math.min(prev, p[idx[k]] * m / (k + 1));
      out[idx[k]] = Math.min(prev, 1);
    }
    return out;
  }
  function analyse(years, values) {
    var c = clean(years, values), mk = mannKendall(c.t, c.x), f = sen(c.t, c.x);
    var ci = senCI(c.t, c.x, mk.variance), d = minDetectable(c.t, c.x);
    var mean = c.x.length ? c.x.reduce(function (a, b) { return a + b; }, 0) / c.x.length : NaN;
    // detectable trend: 3.3 standard errors, the standard error taken from the 95 % interval
    var mdt = (isFinite(ci[0]) && isFinite(ci[1])) ? 3.3 * (ci[1] - ci[0]) / (2 * Z95) : NaN;
    return { n: mk.n, slope: f.slope, intercept: f.intercept, ci_low: ci[0], ci_high: ci[1], p: mk.p, z: mk.z,
      hr_correction: mk.correction, mdt: mdt, noise: d.noise, phi: d.phi, mean: mean };
  }
  var api = { analyse: analyse, benjaminiHochberg: benjaminiHochberg, sen: sen, mannKendall: mannKendall };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.AWStats = api;
})(typeof window !== "undefined" ? window : this);
