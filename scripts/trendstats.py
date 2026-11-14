"""Trend statistics used by BULB-Air. Fixed before looking at any result.

Everything here works on one value per year (for example the mean of one season).

  sen_slope            median of all pairwise slopes (robust to outliers)
  mann_kendall         Mann-Kendall test with the Hamed & Rao (1998) variance correction
                       for year-to-year memory (autocorrelation)
  sen_ci               95 % confidence interval of the Sen slope (Gilbert 1987)
  detectable_trend     smallest trend this record would detect with 90 % probability at
                       the 5 % level: 3.3 standard errors (Weatherhead et al. 1998), with
                       the standard error taken from the same 95 % interval as above
  benjamini_hochberg   false-discovery-rate adjustment for a family of tests
"""
import math

import numpy as np

Z95 = 1.959963984540054


def _clean(years, values):
    t = np.asarray(years, float)
    x = np.asarray(values, float)
    ok = np.isfinite(t) & np.isfinite(x)
    order = np.argsort(t[ok])
    return t[ok][order], x[ok][order]


def _norm_sf(z):
    """Upper tail of the standard normal distribution."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def pairwise_slopes(t, x):
    i, j = np.triu_indices(len(t), 1)
    return np.sort((x[j] - x[i]) / (t[j] - t[i]))


def sen_slope(years, values):
    t, x = _clean(years, values)
    if len(t) < 3:
        return float("nan"), float("nan")
    slope = float(np.median(pairwise_slopes(t, x)))
    intercept = float(np.median(x - slope * t))
    return slope, intercept


def _rank(a):
    """Average ranks (ties share the mean rank)."""
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    r[order] = np.arange(1, len(a) + 1)
    for v in np.unique(a):
        m = a == v
        if m.sum() > 1:
            r[m] = r[m].mean()
    return r


def mann_kendall(years, values, alpha=0.05):
    """Mann-Kendall trend test with Hamed-Rao correction.

    Returns dict: n, S, var_raw, correction (n/n*), z, p, tau.
    p is two-sided: the chance of an |S| this large if there were no trend.
    """
    t, x = _clean(years, values)
    n = len(x)
    if n < 4:
        return dict(n=n, S=0, var_raw=float("nan"), correction=1.0, z=float("nan"),
                    p=float("nan"), tau=float("nan"), var=float("nan"))
    i, j = np.triu_indices(n, 1)
    S = float(np.sign(x[j] - x[i]).sum())
    _, counts = np.unique(x, return_counts=True)
    ties = float((counts * (counts - 1) * (2 * counts + 5)).sum()) if (counts > 1).any() else 0.0
    var_raw = (n * (n - 1) * (2 * n + 5) - ties) / 18.0

    # Hamed & Rao (1998): inflate the variance when detrended ranks are autocorrelated
    slope, _ = sen_slope(t, x)
    resid = x - slope * (t - t[0])
    r = _rank(resid)
    r = r - r.mean()
    denom = float((r * r).sum())
    corr = 1.0
    if denom > 0 and n > 3:
        bound = _z_for(alpha) / math.sqrt(n)
        s = 0.0
        for k in range(1, n - 1):
            rk = float((r[:-k] * r[k:]).sum()) / denom
            if abs(rk) > bound:                      # keep only significant lags
                s += (n - k) * (n - k - 1) * (n - k - 2) * rk
        corr = 1.0 + 2.0 / (n * (n - 1) * (n - 2)) * s
        if corr < 1.0:                               # the correction may only make the test stricter:
            corr = 1.0                               # with ~15 points a "negative memory" is noise
    var = var_raw * corr
    if S > 0:
        z = (S - 1) / math.sqrt(var)
    elif S < 0:
        z = (S + 1) / math.sqrt(var)
    else:
        z = 0.0
    p = 2.0 * _norm_sf(abs(z))
    return dict(n=n, S=S, var_raw=var_raw, correction=corr, var=var, z=z, p=min(1.0, p),
                tau=S / (0.5 * n * (n - 1)))


def _z_for(alpha):
    # only alpha = 0.05 is used; keep a tiny table to avoid a scipy dependency
    return {0.05: Z95, 0.1: 1.6448536269514722, 0.01: 2.5758293035489004}[alpha]


def sen_ci(years, values, var, alpha=0.05):
    """Confidence interval of the Sen slope (Gilbert 1987), using the corrected variance."""
    t, x = _clean(years, values)
    if len(t) < 4 or not np.isfinite(var):
        return float("nan"), float("nan")
    sl = pairwise_slopes(t, x)
    N = len(sl)
    c = _z_for(alpha) * math.sqrt(var)
    lo = int(round((N - c) / 2.0)) - 1
    hi = int(round((N + c) / 2.0))
    lo = max(0, min(N - 1, lo))
    hi = max(0, min(N - 1, hi))
    return float(sl[lo]), float(sl[hi])


def detectable_trend(ci_low, ci_high):
    """Smallest trend (units per year) this record would detect with 90 % probability at the
    5 % level. Weatherhead et al. (1998): the trend must exceed about 3.3 standard errors
    (1.96 for the 5 % level plus 1.28 for 90 % power). We take the standard error from the
    width of the 95 % interval of the Sen slope, so the interval and this threshold always
    rest on the same estimate of the noise."""
    if not (np.isfinite(ci_low) and np.isfinite(ci_high)):
        return float("nan")
    return 3.3 * (ci_high - ci_low) / (2 * Z95)


def noise_and_memory(years, values):
    """Residual noise around the Sen line and its lag-1 autocorrelation (for information).
    Returns (unused, sigma_noise, phi)."""
    t, x = _clean(years, values)
    n = len(x)
    if n < 5:
        return float("nan"), float("nan"), float("nan")
    slope, icpt = sen_slope(t, x)
    resid = x - (icpt + slope * t)
    resid = resid - resid.mean()
    sigma = float(resid.std(ddof=1))
    den = float((resid * resid).sum())
    phi = float((resid[:-1] * resid[1:]).sum() / den) if den > 0 else 0.0
    phi = min(max(phi, 0.0), 0.8)                    # negative memory in a short record is noise
    span = t - t.mean()
    se = sigma / math.sqrt(float((span * span).sum())) * math.sqrt((1 + phi) / (1 - phi))
    return 3.3 * se, sigma, phi


def benjamini_hochberg(pvalues):
    """Adjusted p-values (false discovery rate) for one family of tests."""
    p = np.asarray(pvalues, float)
    out = np.full(len(p), np.nan)
    ok = np.isfinite(p)
    m = int(ok.sum())
    if m == 0:
        return out
    idx = np.where(ok)[0][np.argsort(p[ok])]
    adj = p[idx] * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out[idx] = np.minimum(adj, 1.0)
    return out


def analyse(years, values, alpha=0.05):
    """All numbers for one yearly series."""
    t, x = _clean(years, values)
    mk = mann_kendall(t, x, alpha)
    slope, icpt = sen_slope(t, x)
    lo, hi = sen_ci(t, x, mk.get("var", float("nan")), alpha)
    _, sigma, phi = noise_and_memory(t, x)
    mdt = detectable_trend(lo, hi)
    mean = float(np.mean(x)) if len(x) else float("nan")
    return dict(n=int(mk["n"]), slope=slope, intercept=icpt, ci_low=lo, ci_high=hi,
                p=mk["p"], z=mk["z"], tau=mk["tau"], hr_correction=mk["correction"],
                mdt=mdt, noise=sigma, phi=phi, mean=mean,
                first_year=int(t[0]) if len(t) else None, last_year=int(t[-1]) if len(t) else None)
