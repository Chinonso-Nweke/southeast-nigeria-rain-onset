import json
import pandas as pd
import onset
from download_all import LOCATIONS
from analyse_all import analyse

TOLERANCES = [3, 5, 7, 10, 14]      # dry spell lengths (days) the page lets people choose
WINDOW_DAYS = 30                    # we look at the 30 days after the planting date
PLANT_DATES = pd.date_range("2001-03-01", "2001-06-30")   # 1 March to 30 June


def risk_table(rain):
    """For each planting date and each tolerance: in how many years did a dry spell
    of that length or longer happen within the next 30 days?"""
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


if __name__ == "__main__":
    data = {
        "rule": "From 1 March: first day with at least 20 mm in 3 days and no dry spell of 7+ days (under 1 mm) in the next 30 days",
        "source": "NASA POWER daily PRECTOTCORR, 1981-2024",
        "window_days": WINDOW_DAYS,
        "tolerances": TOLERANCES,
        "risk_dates": [d.strftime("%m-%d") for d in PLANT_DATES],
        "locations": {},
    }
    for name, (lat, lon) in LOCATIONS.items():
        try:
            rain = pd.read_csv(f"rain_{name}.csv", index_col=0, parse_dates=True).iloc[:, 0]
        except FileNotFoundError:
            print(f"Missing rain_{name}.csv, skipping.")
            continue
        a = analyse(rain)
        a["label"] = name.capitalize()
        a["lat"], a["lon"] = lat, lon
        a["years_n"] = int(len(set(rain.index.year)))
        a["risk_counts"] = risk_table(rain)
        data["locations"][name] = a
        print(f"{name}: done")

    with open("results_site.json", "w") as f:
        json.dump(data, f)

    with open("template.html", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved index.html ({len(html) / 1024:.0f} KB). Open it in your browser.")
