import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import pandas as pd
import compare_sources as cc
import download_era5 as de
from test_chirps import synthetic

PAYLOAD = {"daily": {"time": ["2000-01-01", "2000-01-02", "2000-01-03"], "precipitation_sum": [0.0, 12.5, None]}}


class TestEra5(unittest.TestCase):
    def test_parse_handles_missing(self):
        s = de.parse_response(PAYLOAD)
        self.assertEqual(s.loc["2000-01-02"], 12.5)
        self.assertTrue(np.isnan(s.loc["2000-01-03"]))

    def test_download_against_fake_server(self):
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
                self.wfile.write(json.dumps(PAYLOAD).encode())
            def log_message(self, *a): pass
        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        old = (de.FIRST_YEAR, de.LAST_YEAR); de.FIRST_YEAR, de.LAST_YEAR = 2000, 2000
        try:
            import os
            self.assertTrue(de.download("zz_test", 6.46, 7.55, url=f"http://127.0.0.1:{srv.server_port}/"))
            self.assertTrue(os.path.exists("era5_zz_test.csv")); os.remove("era5_zz_test.csv")
        finally:
            de.FIRST_YEAR, de.LAST_YEAR = old; srv.shutdown()


class TestCompare(unittest.TestCase):
    def test_identical_sources_agree_perfectly(self):
        a = synthetic()
        r = cc.compare(a, a.copy())
        self.assertEqual(r["daily_correlation"], 1.0)
        self.assertEqual(r["onset_year_correlation"], 1.0)
        self.assertEqual(r["onset_mean_abs_diff_days"], 0.0)
        self.assertEqual(r["nasa"]["median_onset"], r["other"]["median_onset"])

    def test_only_common_years_are_used(self):
        a = synthetic(start="1981-01-01"); b = synthetic(1, start="1984-01-01", end="2015-12-31")
        r = cc.compare(a, b)
        self.assertEqual(r["years"], "1984 to 2015")

    def test_unrelated_sources_do_not_agree(self):
        r = cc.compare(synthetic(1), synthetic(2))
        self.assertLess(r["daily_correlation"], 0.3)

    def test_a_planted_drop_in_yearly_rain_is_reported(self):
        a = synthetic(3)
        b = a.copy(); b[b.index.year >= 2002] *= 0.7
        r = cc.compare(a, b)
        self.assertLess(r["other"]["annual_change_pct"], -15)
        self.assertGreater(r["nasa"]["annual_change_pct"], -10)



if __name__ == "__main__":
    unittest.main()
