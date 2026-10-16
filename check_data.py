"""Quality checks on the downloaded rainfall files. Prints a report and writes data_report.json.
Exits with an error only for problems that make the results unreliable."""
import json
import sys
import numpy as np
import pandas as pd
from download_all import LOCATIONS
from changepoint import changepoint

MAX_MISSING_SHARE = 0.005       # more than 0.5% missing days is an error
MAX_PLAUSIBLE_DAILY_MM = 400    # a day above this is flagged for a look


def check(name):
    rain = pd.read_csv(f"rain_{name}.csv", index_col=0, parse_dates=True).iloc[:, 0]
    problems, warnings = [], []
    first, last = rain.index.min(), rain.index.max()
    expected = len(pd.date_range(first, last))
    gaps = expected - len(rain)
    missing = int(rain.isna().sum()) + gaps
    if missing / expected > MAX_MISSING_SHARE:
        problems.append(f"{missing} missing days ({missing / expected:.1%})")
    elif missing:
        warnings.append(f"{missing} missing days")
    if (rain < 0).any():
        problems.append("negative rainfall values")
    wettest = rain.idxmax()
    if rain.max() > MAX_PLAUSIBLE_DAILY_MM:
        warnings.append(f"very wet day: {rain.max():.0f} mm on {wettest.date()}")
    totals = rain.groupby(rain.index.year).sum()
    z = (totals - totals.mean()) / totals.std()
    odd = [int(y) for y in z.index[abs(z) > 3]]
    if odd:
        warnings.append(f"unusual yearly totals in {odd}")
    half = len(totals) // 2
    cp = changepoint(totals.index.values, totals.values, n_perm=500)
    return {
        "days": int(len(rain)), "missing_days": missing,
        "wettest_day_mm": round(float(rain.max()), 1), "wettest_day": str(wettest.date()),
        "annual_mm_first_half": round(float(totals.iloc[:half].mean())),
        "annual_mm_second_half": round(float(totals.iloc[half:].mean())),
        "annual_change_year": cp["change_year"], "annual_change_p": cp["p_perm"],
        "problems": problems, "warnings": warnings,
    }


if __name__ == "__main__":
    report, bad = {}, False
    for name in LOCATIONS:
        try:
            r = check(name)
        except FileNotFoundError:
            print(f"{name}: rain_{name}.csv not found. Run download_all.py first.")
            bad = True
            continue
        report[name] = r
        status = "PROBLEM" if r["problems"] else ("note" if r["warnings"] else "ok")
        print(f"{name:<10} {status:<8} days={r['days']} missing={r['missing_days']} "
              f"yearly total {r['annual_mm_first_half']} -> {r['annual_mm_second_half']} mm "
              f"(biggest step in {r['annual_change_year']}, p={r['annual_change_p']})")
        for msg in r["problems"] + r["warnings"]:
            print("           -", msg)
        bad = bad or bool(r["problems"])
    with open("data_report.json", "w") as f:
        json.dump(report, f, indent=1)
    sys.exit(1 if bad else 0)
