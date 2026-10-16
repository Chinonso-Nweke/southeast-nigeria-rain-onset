import numpy as np


def _pettitt_stat(x):
    """Pettitt (1979) statistic. Returns (index k of the last point BEFORE the change, K)."""
    n = len(x)
    s = np.sign(x[None, :] - x[:, None])          # s[i, j] = sign(x_j - x_i)
    u = np.array([s[: t + 1, t + 1:].sum() for t in range(n - 1)])
    k = int(np.argmax(np.abs(u)))
    return k, float(abs(u[k]))


def changepoint(years, values, n_perm=2000, seed=0):
    """Find the single most likely step change in a yearly series.

    Returns the first year of the 'after' period, two p-values (the standard
    approximation and a permutation test), the averages before and after,
    and how much of the year-to-year variation a step explains compared
    with a straight-line trend.
    """
    years = np.asarray(years, float)
    x = np.asarray(values, float)
    n = len(x)
    k, K = _pettitt_stat(x)
    p_approx = min(1.0, 2 * np.exp(-6 * K ** 2 / (n ** 3 + n ** 2)))

    rng = np.random.default_rng(seed)
    hits = sum(_pettitt_stat(rng.permutation(x))[1] >= K for _ in range(n_perm))
    p_perm = (hits + 1) / (n_perm + 1)

    before, after = x[: k + 1], x[k + 1:]
    sst = float(((x - x.mean()) ** 2).sum())
    sse_step = float(((before - before.mean()) ** 2).sum() + ((after - after.mean()) ** 2).sum())
    slope, icpt = np.polyfit(years, x, 1)
    sse_line = float(((x - (slope * years + icpt)) ** 2).sum())
    return {
        "change_year": int(years[k + 1]),
        "p_approx": round(float(p_approx), 4),
        "p_perm": round(float(p_perm), 4),
        "mean_before": round(float(before.mean()), 1),
        "mean_after": round(float(after.mean()), 1),
        "n_before": int(len(before)),
        "n_after": int(len(after)),
        "r2_step": round(1 - sse_step / sst, 3) if sst else 0.0,
        "r2_line": round(1 - sse_line / sst, 3) if sst else 0.0,
    }
