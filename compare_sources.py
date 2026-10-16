"""Compare NASA POWER with a second rainfall source (era5 or chirps) over the same years.
Usage: python compare_sources.py era5      (or: chirps)
Prints a table and writes comparison_<source>.json."""
import json
import sys
import numpy as np
import pandas as pd
from analyse_all import analyse
from changepoint import changepoint
from download_all import LOCATIONS

FIVE_DAY = 5
SOURCES = {"era5": ("era5_{}.csv", "ERA5"), "chirps": ("chirps_{}.csv", "CHIRPS")}


def load(path):
    return pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]


def summarise(rain):
    a = analyse(rain)
    found = [y for y in a["years"] if y["doy"] is not None]
    cp = changepoint([y["year"] for y in found], [y["doy"] for y in found], n_perm=1000)
    totals = rain.groupby(rain.index.year).sum()
    half = len(totals) // 2
    first, second = float(totals.iloc[:half].mean()), float(totals.iloc[half:].mean())
    tcp = changepoint(totals.index.values, totals.values, n_perm=1000)
    return {
        "median_onset": a["median_onset"], "median_doy": a["median_doy"],
        "false_start_pct": a["false_start_pct"], "shift_days": a["shift_days"],
        "trend_days_per_year": a["slope_days_per_year"],
        "step_year": cp["change_year"], "step_p": cp["p_perm"],
        "annual_first_half_mm": round(first), "annual_second_half_mm": round(second),
        "annual_change_pct": round((second - first) / first * 100, 1),
        "annual_step_year": tcp["change_year"], "annual_step_p": tcp["p_perm"],
        "_years": {y["year"]: y["doy"] for y in a["years"]},
        "_totals": totals,
    }


def compare(nasa, other):
    years = sorted(set(nasa.index.year) & set(other.index.year))
    nasa = nasa[nasa.index.year.isin(years)]
    other = other[other.index.year.isin(years)]
    both = pd.concat([nasa, other], axis=1, keys=["n", "c"]).dropna()
    daily_r = float(both["n"].corr(both["c"]))
    five = both.resample(f"{FIVE_DAY}D").sum()
    five_r = float(five["n"].corr(five["c"]))
    n, c = summarise(nasa), summarise(other)
    common = [y for y in years if n["_years"].get(y) is not None and c["_years"].get(y) is not None]
    nd = np.array([n["_years"][y] for y in common], float)
    cd = np.array([c["_years"][y] for y in common], float)
    tn, tc = n.pop("_totals"), c.pop("_totals")
    n.pop("_years"); c.pop("_years")
    return {
        "years": f"{years[0]} to {years[-1]}",
        "daily_correlation": round(daily_r, 2), "five_day_correlation": round(five_r, 2),
        "yearly_total_correlation": round(float(tn.corr(tc)), 2),
        "onset_year_correlation": round(float(np.corrcoef(nd, cd)[0, 1]), 2),
        "onset_mean_abs_diff_days": round(float(np.abs(nd - cd).mean()), 1),
        "mean_annual_mm": {"nasa": round(float(tn.mean())), "other": round(float(tc.mean()))},
        "nasa": n, "other": c,
    }


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "era5"
    if key not in SOURCES:
        raise SystemExit(f"Use one of: {', '.join(SOURCES)}")
    pattern, label = SOURCES[key]
    out = {}
    hdr = f"{'':<10}{'':<8}{'median':<9}{'false':<7}{'shift':<8}{'trend':<8}{'step (p)':<16}{'yearly rain change'}"
    for name in LOCATIONS:
        try:
            out[name] = compare(load(f"rain_{name}.csv"), load(pattern.format(name)))
        except FileNotFoundError as e:
            print(f"{name}: missing file ({e.filename}). Download the {label} data first.")
    if not out:
        raise SystemExit("Nothing to compare.")
    print(f"NASA POWER compared with {label}. Years compared: {next(iter(out.values()))['years']}\n")
    print(hdr)
    for name, r in out.items():
        for src, lab in (("nasa", "NASA"), ("other", label)):
            s = r[src]
            cells = [name if src == "nasa" else "", lab, s["median_onset"][:6], f"{s['false_start_pct']}%",
                     f"{s['shift_days']:+d}d", f"{s['trend_days_per_year']:+.2f}", f"{s['step_year']} ({s['step_p']})",
                     f"{s['annual_first_half_mm']} to {s['annual_second_half_mm']} mm ({s['annual_change_pct']:+.0f}%)"]
            print("".join(c.ljust(w) for c, w in zip(cells, [10, 8, 9, 7, 8, 8, 16, 0])))
    print("\nHow closely the two sources agree:")
    print(f"{'':<10}{'daily r':<10}{'5-day r':<10}{'yearly r':<10}{'start-date r':<14}{'start diff (days)':<19}{'mean yearly mm NASA / ' + label}")
    for name, r in out.items():
        print(f"{name:<10}{r['daily_correlation']:<10}{r['five_day_correlation']:<10}{r['yearly_total_correlation']:<10}"
              f"{r['onset_year_correlation']:<14}{r['onset_mean_abs_diff_days']:<19}{r['mean_annual_mm']['nasa']} / {r['mean_annual_mm']['other']}")
    k = lambda src: sum(r[src]["shift_days"] >= 10 for r in out.values())
    m = lambda src: sum(r[src]["annual_change_pct"] <= -8 for r in out.values())
    N = len(out)
    print(f"\nLater start (second half 10+ days later): NASA {k('nasa')} of {N} places, {label} {k('other')} of {N}.")
    print(f"Yearly rain down 8% or more:               NASA {m('nasa')} of {N} places, {label} {m('other')} of {N}.")
    with open(f"comparison_{key}.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"Saved comparison_{key}.json")
