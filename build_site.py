import json
import os
from datetime import date
import pandas as pd
import onset
from changepoint import changepoint
from check_data import check_series
from download_all import LOCATIONS
from analyse_all import analyse
from compare_sources import compare
from audit import assess, summary_text

TOLERANCES = [3, 5, 7, 10, 14]      # dry spell lengths (days) the page lets people choose
WINDOW_DAYS = 30                    # we look at the 30 days after the planting date
PLANT_DATES = pd.date_range("2001-03-01", "2001-06-30")   # 1 March to 30 June
RECENT_YEARS = 20                   # the "recent" comparison uses the last 20 years
WAIT_COSTS = [0.01, 0.03, 0.06]     # cost of waiting one week, as a share of a failed planting
SOURCES = [                         # key, file pattern, label shown on the page
    ("nasa", "rain_{}.csv", "NASA POWER"),
    ("era5", "era5_{}.csv", "ERA5 (via Open-Meteo)"),
]


def risk_table(rain, years=None):
    """For each planting date and each tolerance: in how many years did a dry spell
    of that length or longer happen within the next 30 days?"""
    if years is None:
        years = sorted(set(rain.index.year))
    counts = {str(t): [0] * len(PLANT_DATES) for t in TOLERANCES}
    for y in years:
        for i, d in enumerate(PLANT_DATES):
            day = pd.Timestamp(year=y, month=d.month, day=d.day)
            window = rain[day + pd.Timedelta(days=1): day + pd.Timedelta(days=WINDOW_DAYS)]
            longest = onset.longest_dry_spell(window)
            for t in TOLERANCES:
                if longest >= t:
                    counts[str(t)][i] += 1
    return counts


def source_block(rain):
    """Everything the page needs for one place under one rainfall source."""
    a = analyse(rain)
    years = sorted(set(rain.index.year))
    a["years_n"] = len(years)
    a["risk_counts"] = risk_table(rain)
    a["risk_counts_recent"] = risk_table(rain, years[-RECENT_YEARS:])
    found = [y for y in a["years"] if y["doy"] is not None]
    a["changepoint"] = changepoint([y["year"] for y in found], [y["doy"] for y in found])
    q = check_series(rain)
    a["qa"] = {k: q[k] for k in ("days", "missing_days", "wettest_day_mm", "wettest_day",
                                  "annual_mm_first_half", "annual_mm_second_half",
                                  "annual_change_year", "annual_change_p")}
    return a


if __name__ == "__main__":
    data = {
        "rule": "From 1 March: first day with at least 20 mm in 3 days and no dry spell of 7+ days (under 1 mm) in the next 30 days",
        "window_days": WINDOW_DAYS,
        "tolerances": TOLERANCES,
        "wait_costs": WAIT_COSTS,
        "recent_n": RECENT_YEARS,
        "risk_dates": [d.strftime("%m-%d") for d in PLANT_DATES],
        "locations": {},
    }
    used = []
    agree_results = {}
    for name, (lat, lon) in LOCATIONS.items():
        series = {}
        for key, pattern, label in SOURCES:
            try:
                series[key] = pd.read_csv(pattern.format(name), index_col=0, parse_dates=True).iloc[:, 0]
            except FileNotFoundError:
                if key == "nasa":
                    print(f"Missing {pattern.format(name)}, skipping {name}.")
                else:
                    print(f"No {label} file for {name}: the page will show NASA POWER only.")
        if "nasa" not in series:
            continue
        common = sorted(set.intersection(*(set(s.index.year) for s in series.values())))
        series = {k: s[s.index.year.isin(common)] for k, s in series.items()}
        loc = {"label": name.capitalize(), "lat": lat, "lon": lon, "src": {}}
        for key, s in series.items():
            loc["src"][key] = source_block(s)
        if "era5" in series:
            c = compare(series["nasa"], series["era5"])
            ass = assess(c, "ERA5")
            loc["agree"] = ass
            agree_results[name] = ass
        data["locations"][name] = loc
        used = [k for k in series]
        first_year, last_year = common[0], common[-1]
        print(f"{name}: done ({', '.join(series)})")

    data["sources"] = used
    data["source_labels"] = {k: lab for k, _, lab in SOURCES if k in used}
    data["first_year"], data["last_year"] = first_year, last_year
    data["recent_first"] = last_year - RECENT_YEARS + 1
    data["trust_summary"] = summary_text(agree_results) if agree_results else ""
    with open("results_site.json", "w") as f:
        json.dump(data, f)

    with open("template.html", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__FIRST__", str(first_year)).replace("__LAST__", str(last_year))
    html = html.replace("__DOWNLOADED__", date.today().strftime("%B %Y"))
    html = html.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved index.html ({len(html) / 1024:.0f} KB). Open it in your browser.")
