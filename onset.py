import pandas as pd

# ---- Our working rule (change these numbers to test other rules) ----
START_MONTH_DAY = "03-01"   # start looking from 1 March
WET_MM = 20                 # at least 20 mm in...
WET_DAYS = 3                # ...3 days in a row
DRY_MM = 1                  # a day under 1 mm counts as dry
DRY_SPELL_DAYS = 7          # a dry spell of 7+ days after the start means a false start
LOOKAHEAD_DAYS = 30         # we check the 30 days after the wet spell


def longest_dry_spell(rain_slice):
    dry = (rain_slice < DRY_MM).astype(int)
    if dry.empty:
        return 0
    return int(dry.groupby((dry == 0).cumsum()).sum().max())


def onset_for_year(rain, year):
    r = rain[str(year)]
    r = r[r.index >= f"{year}-{START_MONTH_DAY}"]
    wet = r.rolling(WET_DAYS).sum()
    triggers = wet[wet >= WET_MM].index           # days that look like a start
    for day in triggers:
        after = r[day + pd.Timedelta(days=1): day + pd.Timedelta(days=LOOKAHEAD_DAYS)]
        if longest_dry_spell(after) < DRY_SPELL_DAYS:
            return day, day != triggers[0]        # True if an earlier trigger failed
    return None, len(triggers) > 0


def all_years(rain):
    rows = []
    for year in sorted(set(rain.index.year)):
        onset, false_start = onset_for_year(rain, year)
        rows.append({"year": year, "onset": onset, "false_start": false_start})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    rain = pd.read_csv("enugu_rain.csv", index_col=0, parse_dates=True).iloc[:, 0]
    res = all_years(rain)
    res["onset_doy"] = pd.to_datetime(res["onset"]).dt.dayofyear
    res.to_csv("onset_by_year.csv", index=False)

    print(res.to_string(index=False))

    found = res.dropna(subset=["onset_doy"])
    median_doy = int(found["onset_doy"].median())
    median_date = (pd.Timestamp("2001-01-01") + pd.Timedelta(days=median_doy - 1)).strftime("%d %B")
    earliest = found.loc[found["onset_doy"].idxmin()]
    latest = found.loc[found["onset_doy"].idxmax()]

    print()
    print(f"Years with an onset found: {len(found)} of {len(res)}")
    print(f"Median onset date: {median_date}")
    print(f"Earliest: {earliest['onset'].date()} ({int(earliest['year'])})")
    print(f"Latest:   {latest['onset'].date()} ({int(latest['year'])})")
    print(f"False start rate: {res['false_start'].mean() * 100:.0f}% of years")