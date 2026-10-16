import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import pandas as pd
import download_chirps as dc

CSV = """time,latitude,longitude,precip
UTC,degrees_north,degrees_east,mm/day
1984-01-01T00:00:00Z,6.425,7.525,1.0
1984-01-01T00:00:00Z,6.425,7.575,3.0
1984-01-02T00:00:00Z,6.425,7.525,NaN
1984-01-02T00:00:00Z,6.425,7.575,4.0
1984-01-03T00:00:00Z,6.425,7.525,-9999.0
1984-01-03T00:00:00Z,6.425,7.575,-9999.0
"""


def synthetic(seed=0, start="1984-01-01", end="2020-12-31"):
    idx = pd.date_range(start, end)
    rng = np.random.default_rng(seed)
    doy = idx.dayofyear.values
    p_wet = np.clip(0.08 + 0.6 * np.exp(-((doy - 220) / 70.0) ** 2), 0, 1)
    return pd.Series(np.where(rng.random(len(idx)) < p_wet, rng.gamma(0.8, 14, len(idx)), 0.0), index=idx)


class TestParse(unittest.TestCase):
    def test_pixels_are_averaged_and_missing_handled(self):
        s, pix = dc.parse_erddap_csv(CSV)
        self.assertEqual(pix, 2)
        self.assertEqual(s.loc["1984-01-01"], 2.0)       # (1 + 3) / 2
        self.assertEqual(s.loc["1984-01-02"], 4.0)       # NaN ignored
        self.assertTrue(np.isnan(s.loc["1984-01-03"]))   # all missing stays missing

    def test_url_has_the_right_ranges(self):
        u = dc.build_url(6.46, 7.55, "1984-01-01", "1988-12-31")
        self.assertIn("chirps20GlobalDailyP05_Lon0360.csv?precip", u)
        self.assertIn("(6.360):1:(6.560)", u)
        self.assertIn("(7.450):1:(7.650)", u)


class TestDownloadAgainstFakeServer(unittest.TestCase):
    def test_download_writes_a_file(self):
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(CSV.encode())
            def log_message(self, *a): pass
        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        old = (dc.FIRST_YEAR, dc.LAST_YEAR)
        dc.FIRST_YEAR, dc.LAST_YEAR = 1984, 1984
        try:
            import os, time
            time.sleep(0.1)
            self.assertTrue(dc.download("zz_test", 6.46, 7.55, base_url=f"http://127.0.0.1:{srv.server_port}/x.csv"))
            self.assertTrue(os.path.exists("chirps_zz_test.csv"))
            os.remove("chirps_zz_test.csv")
        finally:
            dc.FIRST_YEAR, dc.LAST_YEAR = old
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
