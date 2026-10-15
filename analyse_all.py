import json
import numpy as np
import pandas as pd
import onset

from download_all import LOCATIONS


def analyse(rain):
    res = onset.all_years(rain)
    res["onset_doy"] = pd.to_datetime(res["onset"]).dt.dayofyear
    found = res.dropna(subset=["onset_doy"])
    median_doy = int(found["onset_doy"].median())
    median_date = (pd.Timestamp("2001-01-01") + pd.Timedelta(days=median_doy - 1)).strftime("%d %B")
    half = len(res) // 2
    shift = res.iloc[half:]["onset_doy"].mean() - res.iloc[:half]["onset_doy"].mean()
    slope = float(np.polyfit(found["year"], found["onset_doy"], 1)[0])
    monthly = rain.groupby(rain.index.month).sum() / rain.index.year.nunique()
    return {
        "median_onset": median_date,
        "median_doy": median_doy,
        "false_start_pct": round(res["false_start"].mean() * 100),
        "years_found": int(len(found)),
        "years_total": int(len(res)),
        "shift_days": round(float(shift)),
        "slope_days_per_year": round(slope, 2),
        "monthly_mm": [round(float(v), 1) for v in monthly.values],
        "years": [
            {"year": int(r.year),
             "onset": None if pd.isna(r.onset) else r.onset.strftime("%Y-%m-%d"),
             "doy": None if pd.isna(r.onset_doy) else int(r.onset_doy),
             "false_start": bool(r.false_start)}
            for r in res.itertuples()
        ],
    }


if __name__ == "__main__":
    series = {}
    for name in LOCATIONS:
        try:
            series[name] = pd.read_csv(f"rain_{name}.csv", index_col=0, parse_dates=True).iloc[:, 0]
        except FileNotFoundError:
            print(f"Missing rain_{name}.csv. Run download_all.py first.")

    out = {"rule": "From 1 March: first day with at least 20 mm in 3 days and no dry spell of 7+ days (under 1 mm) in the next 30 days",
           "source": "NASA POWER daily PRECTOTCORR, 1981-2024",
           "locations": {}}

    print(f"{'Location':<11}{'Median':<10}{'False starts':<14}{'Shift (days)':<14}{'Trend (d/yr)'}")
    for name, rain in series.items():
        lat, lon = LOCATIONS[name]
        a = analyse(rain)
        a["lat"], a["lon"] = lat, lon
        out["locations"][name] = a
        print(f"{name:<11}{a['median_onset']:<10}{str(a['false_start_pct']) + '%':<14}{a['shift_days']:<14}{a['slope_days_per_year']:+.2f}")

    # Do two towns share the same NASA grid cell? Then their data is identical.
    names = list(series)
    print()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if series[names[i]].equals(series[names[j]]):
                print(f"Note: {names[i]} and {names[j]} have identical data (same grid cell). Count them as one place.")

    with open("results_all.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved results_all.json")
