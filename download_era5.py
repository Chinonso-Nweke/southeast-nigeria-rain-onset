"""Download daily rainfall from ERA5 (via the free Open-Meteo archive) for the same five places.

ERA5 is a global weather reanalysis from the European Centre for Medium-Range Weather
Forecasts (ECMWF). It is made by a different group with a different model from NASA POWER's
source, so agreement between the two is meaningful. It is still a model, not rain gauges, and
its grid is about 25 km.
"""
import sys
import time
import pandas as pd
import requests
from download_all import LOCATIONS, FIRST_YEAR, LAST_YEAR

URL = "https://archive-api.open-meteo.com/v1/archive"
CHUNK_YEARS = 10


def parse_response(data):
    d = data["daily"]
    s = pd.Series(pd.to_numeric(pd.Series(d["precipitation_sum"]), errors="coerce").values,
                  index=pd.to_datetime(d["time"]))
    s[s < 0] = float("nan")
    return s


def download(name, lat, lon, url=URL):
    pieces = []
    for y0 in range(FIRST_YEAR, LAST_YEAR + 1, CHUNK_YEARS):
        y1 = min(y0 + CHUNK_YEARS - 1, LAST_YEAR)
        params = {"latitude": lat, "longitude": lon, "start_date": f"{y0}-01-01", "end_date": f"{y1}-12-31",
                  "daily": "precipitation_sum", "models": "era5", "timezone": "UTC"}
        for attempt in range(1, 6):
            try:
                print(f"{name} {y0}-{y1}: attempt {attempt}...")
                r = requests.get(url, params=params, timeout=120)
                if r.status_code != 200:
                    print(f"   server said {r.status_code}: {r.text[:300]!r}")
                    if r.status_code == 429:
                        time.sleep(60)          # rate limit: wait a minute
                    r.raise_for_status()
                pieces.append(parse_response(r.json()))
                break
            except (requests.exceptions.RequestException, KeyError, ValueError) as e:
                print(f"   problem: {type(e).__name__}: {str(e)[:300]}")
                time.sleep(10)
        else:
            print(f"{name}: FAILED for {y0}-{y1}.")
            return False
        time.sleep(3)
    rain = pd.concat(pieces).sort_index()
    rain.index.name = "date"
    rain.to_csv(f"era5_{name}.csv", header=["precip_mm"])
    print(f"{name}: saved {len(rain)} days, missing {int(rain.isna().sum())}")
    return True


if __name__ == "__main__":
    failed = [n for n, (la, lo) in LOCATIONS.items() if not download(n, la, lo)]
    if failed:
        print("Failed:", ", ".join(failed), "- run the script again later.")
        sys.exit(1)
