import sys
import time
from datetime import date
import requests
import pandas as pd

# Approximate town coordinates. Check them on a map before you publish.
LOCATIONS = {
    "enugu":     (6.46, 7.55),
    "nsukka":    (6.86, 7.40),
    "abakaliki": (6.32, 8.11),
    "onitsha":   (6.14, 6.79),
    "owerri":    (5.48, 7.03),
}

FIRST_YEAR = 1981
LAST_YEAR = date.today().year - 1      # the last complete year

URL = ("https://power.larc.nasa.gov/api/temporal/daily/point"
       "?parameters=PRECTOTCORR&community=AG"
       "&longitude={lon}&latitude={lat}"
       "&start=" + str(FIRST_YEAR) + "0101&end=" + str(LAST_YEAR) + "1231&format=JSON")


def download(name, lat, lon):
    for attempt in range(1, 6):
        try:
            print(f"{name}: attempt {attempt}...")
            r = requests.get(URL.format(lat=lat, lon=lon), timeout=180)
            r.raise_for_status()
            values = r.json()["properties"]["parameter"]["PRECTOTCORR"]
            rain = pd.Series(values)
            rain.index = pd.to_datetime(rain.index, format="%Y%m%d")
            rain = rain.where(rain >= 0)          # -999 means missing
            rain.to_csv(f"rain_{name}.csv")
            print(f"{name}: saved {len(rain)} days, missing {rain.isna().sum()}")
            return True
        except requests.exceptions.RequestException:
            print(f"{name}: network problem, retrying in 10 seconds.")
            time.sleep(10)
    print(f"{name}: FAILED after 5 tries. Run the script again later.")
    return False


if __name__ == "__main__":
    failed = []
    for name, (lat, lon) in LOCATIONS.items():
        if not download(name, lat, lon):
            failed.append(name)
        time.sleep(3)
    if failed:
        print("Failed:", ", ".join(failed))
        sys.exit(1)
